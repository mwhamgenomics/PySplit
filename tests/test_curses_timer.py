from pysplit.client import CursesTimer
from tests import TestPySplit


class TestCursesTimer(TestPySplit):
    def setUp(self):
        self.timer = CursesTimer('a_speedrun')

    def test_init_runs_and_splits(self):
        assert self.timer.current_run is None
        assert self.timer.pb_run is None
        assert self.timer.gold_splits == []
        assert self.timer.pb_splits == []
