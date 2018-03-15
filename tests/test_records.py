import requests
from datetime import datetime
from pysplit.client import records
from tests.data import runs
from tests.test_pysplit import TestPySplit


class TestEntity(TestPySplit):
    def _test_entity(self, cls, initial_entity, update):
        self.assertEqual(requests.get('http://localhost:5000/api/' + cls.schema.name).json(), [])

        r = cls(initial_entity)
        r.push()
        uid = r.data['id']
        self.assertEqual(r.data, cls(uid).data)

        r.data.update(update)
        r.push()
        obs = cls(uid).data
        exp = r.data
        self.assertEqual(obs, exp)

    def test_run(self):
        self._test_entity(
            records.Run,
            {'name': 'a_run', 'runner': 'me', 'start_time': datetime(2018, 2, 15, 12)},
            {'end_time': datetime(2018, 2, 15, 12, 10), 'total_time': 600}
        )

    def test_split(self):
        self._test_entity(
            records.Split,
            {'run_id': 1, 'idx': 1, 'start_time': datetime(2018, 2, 15, 12)},
            {'end_time': datetime(2018, 2, 15, 12, 10), 'total_time': 600}
        )


class TestRecords(TestPySplit):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for _run in runs:
            r = _run.copy()
            splits = r.pop('splits')

            e = records.Run(r)
            e.push()
            run_id = e.data['id']

            for s in splits:
                s['run_id'] = run_id
                if 'end_time' in s:
                    obs = s['end_time'] - s['start_time']
                    assert obs.total_seconds() == s['total_time']

                e = records.Split(s)
                e.push()

            assert splits[0]['start_time'] == r['start_time']
            if 'total_time' in r:
                split_total = sum([s.get('total_time', 0) for s in splits])
                assert split_total == r['total_time']
                assert splits[-1]['end_time'] == r['end_time']

    def test_get_run(self):
        obs = records.get_run(1)
        exp = runs[1]
        self.assertEqual(obs.data['start_time'], exp['start_time'])

    def test_get_best_run(self):
        obs = records.get_best_run('a_run')
        self.assertEqual(obs.data['id'], 3)
        self.assertEqual(obs.data['runner'], 'someone')

    def test_get_pb_run(self):
        obs = records.get_pb_run('a_run', 'me')
        self.assertEqual(obs.data['id'], 2)

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
        o = [{k: v for k, v in s.data.items() if k not in ('id', 'runs.runner', 'runs.name')} for s in obs]
        self.assertEqual(o, exp)

    def test_gold_splits(self):
        self._test_splits(
            records.get_gold_splits('a_run', 'me'),
            [runs[0]['splits'][0], runs[2]['splits'][1], runs[4]['splits'][2]]
        )

        self._test_splits(
            records.get_gold_splits('a_run'),  # community golds
            [runs[0]['splits'][0], runs[3]['splits'][1], runs[4]['splits'][2]]
        )
