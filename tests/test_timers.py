import datetime
from unittest.mock import patch
from pysplit.client import timers, records
from pysplit.config import client_config, server_config
from tests.test_pysplit import TestPySplit
from tests.data import speedruns

patched_now = patch('pysplit.client.timers.now', return_value=records.null_time)
then = datetime.datetime(2017, 3, 24, 19, 1, 1, 500000)  # 1 min, 1.5 sec later
patched_then = patch('pysplit.client.timers.now', return_value=then)
client_config.content = {
    'speedrun_name': 'a_speedrun',
    'nocolour': True,
    'runner_name': 'a_runner',
    'compare': 'a_run'
}

server_config.content = {
    'split_names': {'a_speedrun': ['level_1', 'level_2', 'level_3']}
}


class TestSimpleTimer(TestPySplit):
    def setUp(self):
        self.timer = timers.SimpleTimer()

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
            self.timer._get_splits(),
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
        with patched_then, patch('pysplit.client.timers.SimpleTimer.render_current_time'):
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


class TestCompTimer(TestPySplit):
    timer_cls = timers.ComparisonTimer

    def setUp(self):
        with patch.object(self.timer_cls, 'get_comp_run'), patch('pysplit.client.records.get_gold_splits'):
            self.timer = self.timer_cls()
            self.timer.gold_splits = speedruns[1].splits
            self.timer.comp_run = speedruns[0]

    def test_render_split_comparison(self):
        self.timer.current_split.start_time = records.null_time
        with patched_then:
            self.assertEqual(self.timer.render_current_split_comparison(), '-0:04:28.50')
        with patch('pysplit.client.timers.now', return_value=datetime.datetime(2017, 3, 24, 19, 5, 31, 500000)):
            self.assertEqual(self.timer.render_current_split_comparison(), '+0:00:01.50')

    def test_render_current_time(self):
        self.timer.current_split.start_time = records.null_time
        self.timer.start_time = records.null_time

        with patch('builtins.print') as p:
            with patched_then:
                self.timer.render_current_time()
                p.assert_called_with('level_1  0:01:01.50  0:01:01.50  -0:04:28.50', end='\r')

            with patch('pysplit.client.timers.now', return_value=datetime.datetime(2017, 3, 24, 19, 6)):
                self.timer.render_current_time()
                p.assert_called_with('level_1  0:06:00.00  0:06:00.00  +0:00:30.00', end='\r')
