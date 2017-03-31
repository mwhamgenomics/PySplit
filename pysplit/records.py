import datetime
import sqlite3
import string
from random import choice
from os.path import expanduser

record_db = expanduser('~/.pysplit.sqlite')
db = None
_cursor = None
null_time = datetime.datetime(2017, 3, 24, 19)


def _repr(self, attribs):
    return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%s' % (a, getattr(self, a)) for a in attribs))


def _eq(self, other, attribs):
    return all(getattr(self, a) == getattr(other, a) for a in attribs)


class SpeedRun:
    def __init__(self, name, _id=None, splits=None):
        self.name = name
        self.id = _id
        self.splits = tuple(splits) if splits else self._get_splits()

    def _get_splits(self):
        assert self.id
        cursor().execute('SELECT idx, start_time, end_time FROM splits WHERE run_id=? ORDER BY idx ASC', (self.id,))
        data = cursor().fetchall()
        return tuple(Split(self.name, *s) for s in data)

    @property
    def total_time(self):
        return self.splits[-1].end_time - self.splits[0].start_time

    def push(self):
        cursor().execute(
            'INSERT INTO runs VALUES (?, ?, ?, ?)', (self.id, self.name, self.splits[0].start_time, self.total_time.total_seconds())
        )
        for s in self.splits:
            s._push(self.id)
        db.commit()

    def __repr__(self):
        return _repr(self, ('name', 'id', 'splits'))

    def __eq__(self, other):
        return _eq(self, other, ('name', 'id', 'total_time')) and all(s == o for s, o in zip(self.splits, other.splits))


class Split:
    def __init__(self, run_name, index, start_time=None, end_time=None, split_name=None):
        self.run_name = run_name
        self.name = split_name
        self.index = index
        self.start_time = self._to_datetime(start_time)
        self.end_time = self._to_datetime(end_time)

    @staticmethod
    def _to_datetime(t):
        """
        Convert a string formatted 'yyyy-mm-dd hh:mm:ss.ms' to a datetime if needed.
        :param str t:
        """
        if type(t) is datetime.datetime:
            return t

        elif t and type(t) is str:
            date, time = t.split(' ')
            year, month, day = date.split('-')
            hours, mins, secs = time.split(':')
            if '.' in secs:
                secs, usecs = secs.split('.')
                usecs += '0' * (6 - len(usecs))
            else:
                usecs = 0
            return datetime.datetime(int(year), int(month), int(day), int(hours), int(mins), int(secs), int(usecs))

    @property
    def time_elapsed(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time

    def _push(self, run_id):
        """
        Push split data.
        :param str run_id: speedrun ID to associate with this split
        """
        assert all((self.run_name, self.index, self.start_time, self.end_time))
        cursor().execute(
            'INSERT INTO splits VALUES (?, ?, ?, ?, ?)',
            (generate_id('splits'), run_id, self.index, self.start_time, self.end_time)
        )

    def __repr__(self):
        return _repr(self, ('name', 'index', 'time_elapsed'))

    def __eq__(self, other):
        return _eq(self, other, ('run_name', 'index', 'start_time', 'end_time'))


def generate_id(table_name):
    """
    Return a string not already present in the id column of a given table
    :param str table_name: 'runs' or 'splits'
    """
    new_id = _random_string()

    cursor().execute('SELECT id from %s WHERE id=?' % table_name, (new_id,))
    results = cursor().fetchall()

    if results:
        return generate_id(table_name)

    return new_id


def _random_string(_len=6):
    return ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(_len))


def connect():
    global db
    global _cursor

    db = sqlite3.connect(record_db)
    _cursor = db.cursor()

    _cursor.execute('CREATE TABLE IF NOT EXISTS runs (id text UNIQUE, name text, start_time text, total_time numeric)')
    _cursor.execute(
        'CREATE TABLE IF NOT EXISTS splits ('
        'id text UNIQUE, run_id text REFERENCES runs(id), idx numeric, start_time text, end_time text'
        ')'
    )


def cursor():
    global _cursor
    if _cursor is None:
        connect()
    return _cursor


def get_best_run(name):
    cursor().execute('SELECT id FROM runs WHERE name=? ORDER BY total_time ASC', (name,))
    data = cursor().fetchone()
    if data:
        return SpeedRun(name, data[0])


def _get_average_elapsed_time(splits):
    elapsed_times = [s.time_elapsed.total_seconds() for s in splits]
    avg_secs = sum(elapsed_times) / len(elapsed_times)
    return datetime.timedelta(seconds=avg_secs)


def get_average_run(name):
    """
    Return a hypothetical SpeedRun, where the splits are averages across all previous runs.
    :param str name:
    """
    cursor().execute('SELECT id FROM runs WHERE name=?', (name,))
    data = cursor().fetchall()
    runs = [SpeedRun(name, d[0]) for d in data]

    template_splits = runs[0].splits
    average_splits = []

    for idx in range(len(runs[0].splits)):
        average_splits.append(
            Split(
                name,
                template_splits[idx].index,
                null_time,
                null_time + _get_average_elapsed_time([r.splits[idx] for r in runs])
            )
        )
    return SpeedRun(name, _id='avg_run', splits=average_splits)
