from pysplit import timers, records
from unittest import TestCase
from unittest.mock import patch
from tests.data import speedruns
import datetime


patched_now = patch('pysplit.timers.now', return_value=records.null_time)
then = datetime.datetime(2017, 3, 24, 19, 1, 1, 500000)  # 1 min, 1.5 sec later
patched_then = patch('pysplit.timers.now', return_value=then)


class TestSimpleTimer(TestCase):
    def setUp(self):
        self.timer = timers.SimpleTimer('a_speedrun', ('level_1', 'level_2', 'level_3'), colour=False)

    def test_run(self):
        pass
        # TODO: test SimpleTimer.run

    def test_render_timedelta(self):
        t = records.null_time
        u = then
        self.assertEqual(self.timer.render_timedelta(u - t), '0:01:01.50')
        self.assertEqual(self.timer.render_timedelta(t - u), '-0:01:01.50')

    def test_get_splits(self):
        self.assertEqual(
            self.timer._get_splits(['this', 'that', 'other']),
            [
                records.Split('a_speedrun', 1, split_name='this'),
                records.Split('a_speedrun', 2, split_name='that'),
                records.Split('a_speedrun', 3, split_name='other'),
            ]
        )

    def test_current_split(self):
        self.assertEqual(self.timer.current_split, records.Split('a_speedrun', 1, split_name='this'))

    def test_last_split_end(self):
        self.assertEqual(self.timer.last_split_end, None)
        self.timer.split_idx = 1
        d = datetime.datetime(2017, 3, 24, 17, 1)
        self.timer.splits[0].end_time = d
        self.assertEqual(self.timer.last_split_end, d)

    def test_split(self):
        self.timer.splits[0].start_time = records.null_time
        self.assertEqual(self.timer.split_idx, 0)
        with patched_then, patch('pysplit.timers.SimpleTimer.render_current_time'):
            self.timer.split()
            self.assertEqual(self.timer.split_idx, 1)
            self.assertEqual(self.timer.splits[0].end_time, then)

            self.timer.split_idx = 2
            self.timer.splits[2].start_time = records.null_time
            self.timer.split()
            self.assertEqual(self.timer.done, True)

    def test_render_current_time(self):
        self.timer.splits[0].start_time = records.null_time
        self.timer.start_time = records.null_time

        with patched_then, patch('builtins.print') as p:
            self.timer.render_current_time()
            p.assert_called_with('level_1  0:01:01.50  0:01:01.50', end='\r')


class TestPBTimer(TestCase):
    def setUp(self):
        self.timer = timers.PBTimer('a_speedrun', ('level_1', 'level_2', 'level_3'), colour=False)
        self.timer.pb = speedruns[0]

    def test_render_split_comparison(self):
        self.timer.current_split.start_time = records.null_time
        with patched_then:
            self.assertEqual(self.timer.render_current_split_comparison(), '-0:04:28.50')
        with patch('pysplit.timers.now', return_value=datetime.datetime(2017, 3, 24, 19, 5, 31, 500000)):
            self.assertEqual(self.timer.render_current_split_comparison(), '+0:00:01.50')

    def test_render_current_time(self):
        self.timer.current_split.start_time = records.null_time
        self.timer.start_time = records.null_time

        with patch('builtins.print') as p:
            with patched_then:
                self.timer.render_current_time()
                p.assert_called_with('level_1  0:01:01.50  0:01:01.50  -0:04:28.50  0:05:30.00', end='\r')
            with patch('pysplit.timers.now', return_value=datetime.datetime(2017, 3, 24, 19, 6)):
                self.timer.render_current_time()
                p.assert_called_with('level_1  0:06:00.00  0:06:00.00  +0:00:30.00  0:05:30.00', end='\r')
