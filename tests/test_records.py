from unittest import TestCase
from unittest.mock import Mock, patch
from pysplit import records
from datetime import datetime, timedelta
from tests.data import speedruns

records.record_db = ':memory:'
cursor = records.cursor()


for run in speedruns:
    run.push()


class TestRecords(TestCase):
    def test_get_run(self):
        s = records.SpeedRun('a_speedrun', 'c')
        self.assertEqual(s, speedruns[2])

    def test_get_best_run(self):
        obs = records.get_best_run('a_speedrun')
        self.assertEqual(obs, speedruns[1])

    def test_get_average_run(self):
        obs = records.get_average_run('a_speedrun')
        exp = records.SpeedRun(
            'a_speedrun',
            'avg_run',
            (
                records.Split('a_speedrun', 1, records.null_time, '2017-03-24 19:05:09'),
                records.Split('a_speedrun', 2, records.null_time, '2017-03-24 19:04:42'),
                records.Split('a_speedrun', 3, records.null_time, '2017-03-24 19:05:21')
            )
        )
        self.assertEqual(obs, exp)


class TestSplit(TestCase):
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
        self.speedrun = records.SpeedRun('a_speedrun', 'a', speedruns[0].splits)

    def test_get_splits(self):
        patched_fetch = patch(
            'pysplit.records.cursor',
            return_value=Mock(fetchall=Mock(return_value=((0, '2017-03-24 19:00:00', '2017-03-24 19:00:00'),
                                                          (1, '2017-03-24 19:00:00', '2017-03-24 19:00:00'),
                                                          (2, '2017-03-24 19:00:00', '2017-03-24 19:00:00'))))
        )
        with patched_fetch:
            exp = (
                records.Split('a_speedrun', 0, records.null_time, records.null_time),
                records.Split('a_speedrun', 1, records.null_time, records.null_time),
                records.Split('a_speedrun', 2, records.null_time, records.null_time)
            )
            self.assertEqual(self.speedrun._get_splits(), exp)

    def test_total_time(self):
        self.assertEqual(self.speedrun.total_time, timedelta(minutes=15, seconds=30))

    def test_push(self):
        with patch('pysplit.records.generate_id', return_value='an_id'), patch('pysplit.records.cursor', return_value=Mock()) as p:
            self.speedrun.push()

        for query, data in (
            ('INSERT INTO runs VALUES (?, ?, ?, ?)', ('a', 'a_speedrun', self.speedrun.splits[0].start_time, 930.0)),
            ('INSERT INTO splits VALUES (?, ?, ?, ?, ?)', ('an_id', 'a', 1, self.speedrun.splits[0].start_time, self.speedrun.splits[0].end_time)),
            ('INSERT INTO splits VALUES (?, ?, ?, ?, ?)', ('an_id', 'a', 2, self.speedrun.splits[1].start_time, self.speedrun.splits[1].end_time)),
            ('INSERT INTO splits VALUES (?, ?, ?, ?, ?)', ('an_id', 'a', 3, self.speedrun.splits[2].start_time, self.speedrun.splits[2].end_time)),
        ):
            p.return_value.execute.assert_any_call(query, data)
