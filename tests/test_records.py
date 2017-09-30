from unittest import TestCase
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from pysplit.client import records
from pysplit.config import client_config
from tests.test_pysplit import TestPySplit
from tests.data import speedruns

client_config.content = {'runner_name': 'a_runner'}


class TestRecords(TestPySplit):
    def test_get_run(self):
        obs = records.get_run(2)
        exp = speedruns[1]
        self.assertEqual(obs, exp)

    def test_get_best_run(self):
        obs = records.get_best_run('a_speedrun')
        self.assertEqual(obs, speedruns[1])

    def test_get_pb_run(self):
        obs = records.get_pb_run('a_speedrun', 'a_runner')
        self.assertEqual(obs, speedruns[1])

    def test_get_average_run(self):
        obs = records.get_average_run('a_speedrun')
        exp = records.SpeedRun(
            'a_speedrun',
            'a_runner',
            'avg_run',
            (
                records.Split('a_speedrun', 1, records.null_time, '2017-03-24 19:04:58.5'),
                records.Split('a_speedrun', 2, records.null_time, '2017-03-24 19:04:48'),
                records.Split('a_speedrun', 3, records.null_time, '2017-03-24 19:05:16.5')
            )
        )
        self.assertEqual(obs, exp)

    def test_get_gold_splits(self):
        obs = records.get_gold_splits('a_speedrun')
        exp = [
            records.Split('a_speedrun', 1, '2017-03-22 11:40:53', '2017-03-22 11:45:50'),
            records.Split('a_speedrun', 2, '2017-03-21 13:06:45', '2017-03-21 13:11:10'),
            records.Split('a_speedrun', 3, '2017-03-22 11:51:01', '2017-03-22 11:56:14')
        ]
        self.assertEqual(obs, exp)


class TestSplit(TestPySplit):
    def setUp(self):
        self.split = records.Split('a_speedrun', 0, records.null_time, split_name='level_1')

    def test_to_datetime(self):
        self.assertEqual(self.split._to_datetime(records.null_time), records.null_time)
        self.assertEqual(self.split._to_datetime('2017-03-24 19:01:01'), datetime(2017, 3, 24, 19, 1, 1))
        self.assertEqual(self.split._to_datetime('2017-03-24 19:01:01.1337'), datetime(2017, 3, 24, 19, 1, 1, 133700))

    def test_time_elapsed(self):
        self.assertEqual(self.split.time_elapsed, None)
        self.split.end_time = datetime(2017, 3, 24, 19, 1, 1)
        self.assertEqual(self.split.time_elapsed, timedelta(minutes=1, seconds=1))


class TestSpeedRun(TestCase):
    def setUp(self):
        self.speedrun = records.SpeedRun('a_speedrun', 'a_runner', 'a', speedruns[0].splits)

    def test_get_splits(self):
        patched_get = patch(
            'requests.get',
            return_value=Mock(
                json=Mock(
                    return_value=[
                        {'id': 1337, 'run_id': 0, 'run_name': 'a_run', 'idx': 0, 'start_time': '2017-03-24 19:00:00', 'end_time': '2017-03-24 19:00:00'},
                        {'id': 1338, 'run_id': 0, 'run_name': 'a_run', 'idx': 1, 'start_time': '2017-03-24 19:00:00', 'end_time': '2017-03-24 19:00:00'},
                        {'id': 1339, 'run_id': 0, 'run_name': 'a_run', 'idx': 2, 'start_time': '2017-03-24 19:00:00', 'end_time': '2017-03-24 19:00:00'}
                    ]
                )
            )
        )
        with patched_get:
            exp = (
                records.Split('a_speedrun', 0, records.null_time, records.null_time),
                records.Split('a_speedrun', 1, records.null_time, records.null_time),
                records.Split('a_speedrun', 2, records.null_time, records.null_time)
            )
            self.assertEqual(self.speedrun._get_splits(), exp)

    def test_total_time(self):
        self.assertEqual(self.speedrun.total_time, timedelta(minutes=15, seconds=30))

    def test_push(self):
        with patch('requests.post', return_value=Mock(json=Mock(return_value={'id': 'an_id'}))) as p:
            self.speedrun.push()

        p.assert_any_call(
            'http://localhost:5000/api/runs',
            json={
                'name': 'a_speedrun',
                'runner': 'a_runner',
                'start_time': '2017-03-20 12:00:00',
                'total_time': 930.0
            }
        )

        for idx, start_time, end_time in (
            (1, self.speedrun.splits[0].start_time, self.speedrun.splits[0].end_time),
            (2, self.speedrun.splits[1].start_time, self.speedrun.splits[1].end_time),
            (3, self.speedrun.splits[2].start_time, self.speedrun.splits[2].end_time),
        ):
            p.assert_any_call(
                'http://localhost:5000/api/splits',
                json={
                    'run_id': 'an_id',
                    'run_name': 'a_speedrun',
                    'idx': idx,
                    'start_time': str(start_time),
                    'end_time': str(end_time)
                }
            )
