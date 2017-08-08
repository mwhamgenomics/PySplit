from os.path import join, dirname, abspath
from unittest import TestCase
from unittest.mock import Mock
from pysplit.config import Config


class TestConfig(TestCase):
    def setUp(self):
        self.cfg = Config()
        self.cfg._cmd_args = Mock(
            config=join(dirname(dirname(abspath(__file__))), 'example_pysplit.yaml'),
            speedrun_name='a_run'
        )

    def test_resolve_split_names(self):
        exp = ['level1', 'level2', 'level3']
        self.assertEqual(self.cfg._resolve_split_names('a_run'), exp)
        self.assertEqual(self.cfg._resolve_split_names('another_run'), exp)
