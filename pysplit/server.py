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
    cursor.execute('SELECT id from %s ORDER BY id DESC LIMIT 1' % table_name,)
    data = cursor.fetchone()

    if data:
        latest_id = int(data[0])
    else:
        latest_id = 0

    return latest_id + 1


@app.route('/')
def main_page():
    return flask.render_template('main.html')


@app.route('/api/run_categories')
def run_categories():
    return flask.jsonify(list(cfg['split_names']))


@app.route('/api/split_names')
def split_names():
    run_name = flask.request.args.get('run_name')
    if not run_name:
        flask.abort(400, 'This endpoint requires a run_name argument')

    _split_names = cfg['split_names'].get(run_name)
    if not _split_names:
        flask.abort(404, 'No splits configured for %s' % run_name)
    return flask.jsonify(_split_names)


def _build_query(query, params=(), order_stmnt=''):
    keys = []
    vals = []

    for k in params:
        v = flask.request.args.get(k)
        if v:
            keys.append(k)
            vals.append(v)

    if keys:
        query += 'WHERE ' + ' AND '.join(['%s=?' % k for k in keys])

    query += order_stmnt
    return query, vals


def _handle_insert(table, colnames):
    payload = flask.request.json.copy()
    payload['id'] = generate_id(table)
    _colnames = ('id',) + colnames
    assert sorted(payload) == sorted(_colnames), 'Payload did not contain all required fields'
    expr = 'INSERT INTO %s VALUES (%s)' % (table, ', '.join('?' * len(_colnames)))
    vals = tuple(payload[k] for k in _colnames)
    cursor.execute(expr, vals)
    db.commit()
    app.logger.debug('Inserted into %s: %s', table, payload)
    return flask.jsonify(payload)


@app.route('/api/runs', methods=['GET', 'POST'])
def runs():
    if flask.request.method == 'POST':
        return _handle_insert('runs', ('name', 'runner', 'start_time', 'total_time'))

    query, args = _build_query(
        'SELECT id, name, runner, start_time, total_time from runs ',
        ('name', 'runner', 'id'),
        ' ORDER BY total_time ASC'
    )

    if not args:
        cursor.execute('SELECT DISTINCT name from runs')
        data = cursor.fetchall()
        return flask.jsonify([d[0] for d in data])

    cursor.execute(query, args)
    retmax = flask.request.args.get('retmax')
    if retmax:
        data = cursor.fetchmany(int(retmax))
    else:
        data = cursor.fetchall()

    data = [
        {'id': _id, 'name': name, 'runner': runner, 'start_time': start_time, 'total_time': total_time}
        for _id, name, runner, start_time, total_time in data
    ]
    return flask.jsonify(data)


@app.route('/api/splits', methods=['GET', 'POST'])
def splits():
    if flask.request.method == 'POST':
        return _handle_insert('splits', ('run_id', 'run_name', 'idx', 'start_time', 'end_time'))

    query, args = _build_query(
        'SELECT id, run_id, run_name, idx, start_time, end_time FROM splits ',
        ('run_id', 'run_name')
    )
    if not args:
        flask.abort(400, 'This endpoint requires a run_id or run_name argument')

    cursor.execute(query, args)
    data = cursor.fetchall()

    data = [
        {'id': _id, 'run_id': _run_id, 'run_name': run_name, 'idx': idx, 'start_time': start_time, 'end_time': end_time}
        for _id, _run_id, run_name, idx, start_time, end_time in data
    ]
    return flask.jsonify(data)


def main(record_db):
    global db
    global cursor
    global server

    f = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s', '%Y-%b-%d %H:%M:%S')
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.INFO)
    h.setFormatter(f)

    for logger in {log.access_log, log.app_log, log.gen_log, app.logger}:
        logger.addHandler(h)
        logger.setLevel(logging.INFO)

    db = sqlite3.connect(record_db)
    cursor = db.cursor()

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS runs ('
        'id numeric UNIQUE, name text, runner text, start_time text, total_time numeric'
        ')'
    )
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS splits ('
        'id numeric UNIQUE, '
        'run_id numeric REFERENCES runs(id), '
        'run_name text REFERENCES runs(name), '
        'idx numeric, '
        'start_time text, '
        'end_time text'
        ')'
    )

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
