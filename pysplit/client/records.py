import requests
import datetime
from pysplit.config import client_config as cfg

db = None
_cursor = None
null_time = datetime.datetime(2017, 3, 24, 19)


def _repr(self, attribs):
    return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%s' % (a, getattr(self, a)) for a in attribs))


def _eq(self, other, attribs):
    return all(getattr(self, a) == getattr(other, a) for a in attribs)


class SpeedRun:
    def __init__(self, name, runner, _id=None, splits=None):
        self.name = name
        self.runner = runner
        self.id = _id
        self.splits = tuple(splits) if splits else self._get_splits()

    def _get_splits(self):
        assert self.id
        data = requests.get('http://localhost:5000/api/splits', params={'run_id': self.id}).json()
        return tuple(
            Split(self.name, d['idx'], d.get('start_time'), d.get('end_time'))
            for d in data
        )

    @property
    def total_time(self):
        return self.splits[-1].end_time - self.splits[0].start_time

    def push(self):
        r = requests.post(
            'http://localhost:5000/api/runs',
            json={
                'name': self.name,
                'runner': self.runner,
                'start_time': str(self.splits[0].start_time),
                'total_time': self.total_time.total_seconds()
            }
        )
        new_run_id = r.json()['id']
        for s in self.splits:
            s._push(new_run_id)

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
        requests.post(
            'http://localhost:5000/api/splits',
            json={
                'run_id': run_id,
                'run_name': self.run_name,
                'idx': self.index,
                'start_time': str(self.start_time),
                'end_time': str(self.end_time)
            }
        )

    def __repr__(self):
        return _repr(self, ('name', 'run_name', 'index', 'time_elapsed'))

    def __eq__(self, other):
        return _eq(self, other, ('run_name', 'index', 'start_time', 'end_time'))


def get_run(run_id):
    data = requests.get('http://localhost:5000/api/runs', params={'id': run_id}).json()[0]
    if data:
        return SpeedRun(data['name'], data['runner'], data['id'])


def get_pb_run(name, runner):
    data = requests.get('http://localhost:5000/api/runs', params={'name': name, 'runner': runner}).json()[0]
    if data:
        return SpeedRun(data['name'], data['runner'], data['id'])


def get_best_run(name):
    data = requests.get('http://localhost:5000/api/runs', params={'name': name}).json()[0]
    if data:
        return SpeedRun(data['name'], data['runner'], data['id'])


def _get_average_elapsed_time(splits):
    elapsed_times = [s.time_elapsed.total_seconds() for s in splits]
    avg_secs = sum(elapsed_times) / len(elapsed_times)
    return datetime.timedelta(seconds=avg_secs)


def get_average_run(name):
    """
    Return a hypothetical SpeedRun, where the splits are averages across all previous runs.
    :param str name:
    """
    data = requests.get('http://localhost:5000/api/runs', params={'name': name, 'runner': cfg['runner_name']}).json()
    runs = [SpeedRun(name, cfg['runner_name'], d['id']) for d in data]

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
    return SpeedRun(name, cfg['runner_name'], _id='avg_run', splits=average_splits)


def get_gold_splits(name):
    data = requests.get('http://localhost:5000/api/splits', params={'run_name': name}).json()
    gold_splits = {}

    for d in data:
        s = Split(name, d['idx'], d.get('start_time'), d.get('end_time'), d.get('split_name'))
        i = s.index
        if i not in gold_splits or s.time_elapsed < gold_splits[i].time_elapsed:
            gold_splits[i] = s

    return [gold_splits[k] for k in sorted(gold_splits)]
