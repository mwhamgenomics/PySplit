from os.path import join, dirname, abspath
from unittest import TestCase
from unittest.mock import Mock
from pysplit.config import ServerConfig


class TestConfig(TestCase):
    def setUp(self):
        self.cfg = ServerConfig()
        self.cfg._cmd_args = Mock(
            config=join(dirname(dirname(abspath(__file__))), 'example_pysplit.yaml'),
        )

    def test_configure(self):
        exp = {
            'a_speedrun': ['level_1', 'level_2', 'level_3'],
            'another_run': ['level_1', 'level_2', 'level_3'],
        }
        self.cfg.configure()
        self.assertEqual(self.cfg['split_names'], exp)
