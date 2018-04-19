import json
from datetime import datetime
from unittest import TestCase
from pysplit import server
from tests.data import runs


class TestServer(TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        server.app.testing = True
        cls.client = server.app.test_client()
        cls.client.get()
        server.init_db(':memory:')

    @classmethod
    def get(cls, endpoint):
        r = cls.client.get('/api/' + endpoint)
        return json.loads(r.data.decode('utf-8'))

    @staticmethod
    def _update(method, endpoint, data):
        r = method(
            '/api/' + endpoint,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        if not 200 <= r.status_code <= 299:
            raise AssertionError('%s got response %s: %s' % (method, r.status, r.data))
        return r.data

    @classmethod
    def post(cls, endpoint, data):
        return cls._update(cls.client.post, endpoint, data)

    @classmethod
    def patch(cls, endpoint, data):
        return cls._update(cls.client.patch, endpoint, data)


class TestSchemaEndpoint(TestServer):
    def _test_endpoint(self, endpoint, initial_entity, update):
        self.assertEqual(self.get(endpoint), [])
        self.post(endpoint, initial_entity)

        obs = self.get(endpoint)[0]
        initial_entity['id'] = update['id'] = obs['id']
        self.assertEqual(initial_entity, obs)

        initial_entity.update(update)
        self.patch(endpoint, update)
        obs = self.get(endpoint)[0]
        self.assertEqual(initial_entity, obs)

    def test_run(self):
        self._test_endpoint(
            'runs',
            {'name': 'a_run', 'runner': 'me', 'start_time': '2018-02-15 12:00:00'},
            {'end_time': '2018-02-15 12:10:00', 'total_time': 600}
        )

    def test_split(self):
        self._test_endpoint(
            'splits',
            {'run_id': 1, 'idx': 1, 'start_time': '2018-02-15 12:00:00'},
            {'end_time': '2018-02-15 12:10:00', 'total_time': 600}
        )


class TestRecords(TestServer):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        datefmt = '%Y-%m-%d %H:%M:%S'  # TODO: match up with records.Entity

        for _run in runs:
            r = _run.copy()
            splits = r.pop('splits')

            cls.post('runs', r)
            run_id = r['id']

            for s in splits:
                s['run_id'] = run_id
                if 'end_time' in s:
                    obs = datetime.strptime(s['end_time'], datefmt) - datetime.strptime(s['start_time'], datefmt)
                    assert obs.total_seconds() == s['total_time']

                cls.post('splits', s)

            assert splits[0]['start_time'] == r['start_time']
            if 'total_time' in r:
                split_total = sum([s.get('total_time', 0) for s in splits])
                assert split_total == r['total_time']
                assert splits[-1]['end_time'] == r['end_time']

    def test_get_run(self):
        obs = self.get('runs?id=1')[0]
        exp = runs[1]
        self.assertEqual(obs['start_time'], exp['start_time'])

    def test_get_best_run(self):
        obs = self.get('runs?name=a_run&order_by=total_time')[0]
        self.assertEqual(obs['id'], 3)
        self.assertEqual(obs['runner'], 'someone')

    def test_get_pb_run(self):
        obs = self.get('runs?name=a_run&runner=me&order_by=total_time')[0]
        self.assertEqual(obs['id'], 2)

    # def test_get_average_run(self):
    #     obs = records.get_average_run('a_speedrun')
    #     exp = records.SpeedRun(
    #         'a_speedrun',
    #         'a_runner',
    #         'avg_run',
    #         (
    #             records.Split('a_speedrun', 1, records.null_time, '2017-03-24 19:04:58.5'),
    #             records.Split('a_speedrun', 2, records.null_time, '2017-03-24 19:04:48'),
    #             records.Split('a_speedrun', 3, records.null_time, '2017-03-24 19:05:16.5')
    #         )
    #     )
    #     self.assertEqual(obs, exp)

    def _test_splits(self, obs, exp):
        o = [{k: v for k, v in s.items() if k not in ('id', 'runs.runner', 'runs.name')} for s in obs]
        self.assertEqual(o, exp)

    def test_gold_splits(self):
        self._test_splits(
            self.get('gold_splits/a_run?runs.runner=me'),
            [runs[0]['splits'][0], runs[2]['splits'][1], runs[4]['splits'][2]]
        )

        self._test_splits(
            self.get('gold_splits/a_run'),  # community golds
            [runs[0]['splits'][0], runs[3]['splits'][1], runs[4]['splits'][2]]
        )
