from unittest import TestCase
from pysplit.client import CursesTimer, cfg


class TestCursesTimer(TestCase):
    def setUp(self):
        cfg.content = {
            'positional': 'a_run',
            'split_names': {
                'a_run': ['this', 'that', 'other'],
            },
            'runner_name': 'me',
            'pb_sound': None,
            'gold_sound': None,
            'controls': {'advance': 'space', 'stop_reset': 'backspace', 'quit': 'q'}
        }
        self.timer = CursesTimer()

    def test_init_runs_and_splits(self):
        assert self.timer.current_run is None
        assert self.timer.pb_run is None
        assert self.timer.gold_splits == []
        assert self.timer.pb_splits == []
