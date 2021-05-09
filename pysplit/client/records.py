import requests
import datetime
from os.path import join
from pysplit.server import runs, splits
from pysplit.config import cfg


class PySplitClientError(Exception):
    pass


def request(method, endpoint, **kwargs):
    try:
        r = requests.request(method, join(cfg.query('client', 'server_url', ret_default='http://localhost:5000'), 'api', endpoint), **kwargs)
        return r.json()
    except requests.ConnectionError:
        raise PySplitClientError('No server found') from None


def _repr(self, attribs):
    return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%s' % (a, getattr(self, a)) for a in attribs))


def _eq(self, other, attribs):
    return all(getattr(self, a) == getattr(other, a) for a in attribs)


class Entity:
    schema = None
    datefmt = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, data=None):
        if isinstance(data, int):  # uid argument
            self.data = request('get', self.schema.name, params={'id': data})[0]
        else:  # json argument
            self.data = data.copy() or {}

        for k, v in self.data.items():
            if k in self.schema.datetimes and isinstance(v, str):
                self.data[k] = datetime.datetime.strptime(v, self.datefmt)

    def serialise(self):
        serialised_entity = {}
        for k, v in self.data.items():
            if k not in self.schema.field_names:
                continue

            if k in self.schema.datetimes:
                v = v.strftime(self.datefmt)

            serialised_entity[k] = v

        return serialised_entity

    def post(self):
        return request('post', self.schema.name, json=self.serialise())['id']

    def patch(self):
        return request('patch', self.schema.name, json=self.serialise())

    def push(self):
        if 'id' in self.data:
            self.patch()
        else:
            uid = self.post()
            self.data['id'] = uid

    @property
    def elapsed_time(self):
        if not self.data.get('end_time'):
            return None

        return self.data['end_time'] - self.data['start_time']


class Run(Entity):
    schema = runs


class Split(Entity):
    schema = splits


def get_run(run_id):
    data = request('get', 'runs', params={'id': run_id})
    if data:
        return Run(data[0])


def get_pb_run(name, runner):
    data = request('get', 'runs', params={'name': name, 'runner': runner, 'order_by': 'total_time'})
    if data:
        return Run(data[0])


def get_best_run(name):
    data = request('get', 'runs', params={'name': name, 'order_by': 'total_time'})
    if data:
        return Run(data[0])


def get_pb_splits(name, runner):
    r = get_pb_run(name, runner)
    if r:
        data = request('get', 'splits', params={'run_id': r.data['id'], 'order_by': 'idx'})
        return [Split(d) for d in data]


def get_gold_splits(run_name, runner=None):
    params = {}
    if runner:
        params['runs.runner'] = runner

    data = request('get', 'gold_splits/' + run_name, params=params)
    return [Split(d) for d in data]


# def _get_average_elapsed_time(splits):
#     elapsed_times = [s.time_elapsed.total_seconds() for s in splits]
#     avg_secs = sum(elapsed_times) / len(elapsed_times)
#     return datetime.timedelta(seconds=avg_secs)
#
#
# def get_average_run(name):
#     """
#     Return a hypothetical SpeedRun, where the splits are averages across all previous runs.
#     :param str name:
#     """
#     data = request('get', 'runs', params={'name': name, 'runner': cfg['runner_name']})
#     runs = [SpeedRun(name, cfg['runner_name'], d['id']) for d in data]
#
#     template_splits = runs[0].splits
#     average_splits = []
#
#     for idx in range(len(runs[0].splits)):
#         average_splits.append(
#             Split(
#                 name,
#                 template_splits[idx].index,
#                 null_time,
#                 null_time + _get_average_elapsed_time([r.splits[idx] for r in runs])
#             )
#         )
#     return SpeedRun(name, cfg['runner_name'], _id='avg_run', splits=average_splits)
