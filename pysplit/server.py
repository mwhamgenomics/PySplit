import sys
import flask
import sqlite3
import logging
from tornado import ioloop, httpserver, wsgi, log
from pysplit.config import server_config as cfg

app = flask.Flask(__name__)
db = None
cursor = None
server = None


def generate_id(table_name):
    """
    Return a string not already present in the id column of a given table
    :param str table_name: 'runs' or 'splits'
    """
    cursor.execute('SELECT id FROM %s ORDER BY id DESC LIMIT 1' % table_name)
    data = cursor.fetchone()

    if data:
        latest_id = int(data[0])
    else:
        latest_id = -1

    return latest_id + 1


@app.route('/')
def main_page():
    return flask.render_template('main.html')


@app.route('/api/run_categories')
def run_categories():
    cursor.execute('SELECT name FROM runs')
    return flask.jsonify(list(set(line[0] for line in cursor.fetchall())))


@app.route('/api/gold_splits/<run_name>')
def gold_splits(run_name):
    _gold_splits = []

    kwargs = {'runs.name': run_name, 'joined_fields': 'runs.name,runs.runner', 'max_results': 1}
    runner = flask.request.args.get('runs.runner')
    if runner:
        kwargs['runs.runner'] = runner
        kwargs['joined_fields'] = 'runs.runner'

    data = splits.select(order_by='-idx', **kwargs)
    if not data:
        return flask.jsonify(_gold_splits)

    max_idx = data[0]['idx']
    for i in range(max_idx + 1):
        g = splits.select(order_by='total_time', idx=i, **kwargs)
        if g:
            _gold_splits.append(g[0])

    return flask.jsonify(_gold_splits)


@app.route('/api/completion_ratio')
def completion_ratio():
    run_name = flask.request.args.get('run_name')
    if not run_name:
        flask.abort(400, 'This endpoint requires a run_name argument')

    cursor.execute('SELECT count(id), count(total_time) FROM runs WHERE name=?', (run_name,))
    total, completed = cursor.fetchone()
    return flask.jsonify({'total': total, 'completed': completed})


@app.route('/api/split_names')
def split_names():
    run_name = flask.request.args.get('run_name')
    if not run_name:
        flask.abort(400, 'This endpoint requires a run_name argument')

    _split_names = cfg['split_names'].get(run_name)
    if not _split_names:
        flask.abort(404, 'No split names configured for %s' % run_name)
    return flask.jsonify(_split_names)


@app.route('/api/runs', methods=['GET', 'POST', 'PATCH'])
def api_runs():
    if flask.request.method == 'POST':
        return runs.insert()

    if flask.request.method == 'PATCH':
        return runs.update()

    if not any(flask.request.args.get(f.name) for f in runs.schema):
        cursor.execute('SELECT DISTINCT name from runs')
        data = cursor.fetchall()
        return flask.jsonify([d[0] for d in data])

    return flask.jsonify(runs.select())


@app.route('/api/splits', methods=['GET', 'POST', 'PATCH'])
def api_splits():
    if flask.request.method == 'POST':
        return splits.insert()

    if flask.request.method == 'PATCH':
        return splits.update()

    return flask.jsonify(splits.select())


class Field:
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type


class Table:
    def __init__(self, name, schema, reference):
        self.name = name
        self.schema = schema
        self.reference = reference
        self.field_names = tuple(f.name for f in self.schema)
        self.datetimes = tuple(f.name for f in self.schema if f.data_type == 'datetime')

    def select(self, **request_args):
        fields = ['%s.%s' % (self.name, f.name) for f in self.schema]
        sql_where = ''
        sql_join = ''
        sql_order_by = ''

        request_args.update({k: v for k, v in flask.request.args.items() if k not in request_args})
        joined_fields = request_args.pop('joined_fields', None)
        order_by = request_args.pop('order_by', None)
        retmax = request_args.pop('max_results', None)

        if joined_fields:
            joined_fields = joined_fields.split(',')
            fields += joined_fields
            sql_join = ' INNER JOIN %s ON %s=%s' % self.reference

        sql_query = 'SELECT %s FROM %s' % (', '.join(fields), self.name)

        wheres = []
        for k, v in request_args.items():
            if '.' not in k:
                k = '%s.%s' % (self.name, k)
            wheres.append((k, v))

        if order_by:
            direction = 'ASC'
            if order_by.startswith('-'):
                order_by = order_by[1:]
                direction = 'DESC'

            sql_order_by = ' ORDER BY %s.%s %s' % (self.name, order_by, direction)

        if wheres:
            sql_where = ' WHERE ' + ' AND '.join('%s=?' % k for k, v in wheres)
            if order_by:
                sql_where += ' AND %s.%s IS NOT NULL' % (self.name, order_by)

        sql = sql_query + sql_join + sql_where + sql_order_by
        app.logger.debug('"%s" - %s', sql, wheres)

        try:
            cursor.execute(sql, tuple(v for k, v in wheres))
        except sqlite3.OperationalError:
            raise

        if retmax:
            data = cursor.fetchmany(int(retmax))
        else:
            data = cursor.fetchall()

        return [
            {k.replace(self.name + '.', ''): v for k, v in zip(fields, d) if v is not None}
            for d in data
        ]

    def insert(self):
        fields = [f.name for f in self.schema]
        payload = flask.request.json.copy()
        payload['id'] = generate_id(self.name)

        expr = 'INSERT INTO %s VALUES (%s)' % (self.name, ', '.join('?' * len(fields)))
        vals = tuple(payload.get(k) for k in fields)
        cursor.execute(expr, vals)
        db.commit()
        app.logger.debug('Inserted into %s: %s', self.name, payload)
        return flask.jsonify(payload)

    def update(self):
        payload = flask.request.json.copy()
        keys = []
        vals = []
        uid = payload.pop('id', None)
        assert uid is not None, 'Need to know the id of the field to update'
        for k, v in payload.items():
            keys.append(k)
            vals.append(v)

        expr = 'UPDATE %s SET %s WHERE id=?;' % (self.name, ', '.join('%s=?' % k for k in keys))
        cursor.execute(expr, tuple(vals) + (uid,))
        db.commit()
        app.logger.debug('Updated %s: %s', self.name, payload)
        return flask.jsonify(payload)


runs = Table(
    name='runs',
    schema=(
        Field('id',         'numeric UNIQUE'),
        Field('name',       'text'),
        Field('runner',     'text'),
        Field('start_time', 'datetime'),
        Field('end_time',   'datetime'),
        Field('total_time', 'numeric')
    ),
    reference=('splits', 'runs.id', 'splits.run_id')
)

splits = Table(
    name='splits',
    schema=(
        Field('id',         'numeric UNIQUE'),
        Field('run_id',     'numeric REFERENCES runs(id)'),
        Field('idx',        'numeric'),
        Field('start_time', 'datetime'),
        Field('end_time',   'datetime'),
        Field('total_time', 'numeric')
    ),
    reference=('runs', 'splits.run_id', 'runs.id')
)


def init_db(record_db):
    global db
    global cursor

    db = sqlite3.connect(record_db)
    cursor = db.cursor()

    for t in (runs, splits):
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS %s (%s)' % (
                t.name,
                ', '.join('%s %s' % (f.name, f.data_type) for f in t.schema)
            )
        )


def main(record_db):
    global server

    f = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s', '%Y-%b-%d %H:%M:%S')
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.INFO)
    h.setFormatter(f)

    for logger in {log.access_log, log.app_log, log.gen_log, app.logger}:
        logger.addHandler(h)
        logger.setLevel(logging.INFO)

    init_db(record_db)

    wsgi_container = wsgi.WSGIContainer(app)
    server = httpserver.HTTPServer(wsgi_container)
    server.listen(5000)
    ioloop.IOLoop.instance().start()


def stop(sig=None, frame=None):
    server.stop()
    ioloop.IOLoop.instance().stop()
    return 0


def advance(sig=None, frame=None):
    pass


if __name__ == '__main__':
    main(server.cfg['record_db'])
