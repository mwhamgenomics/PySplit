from os.path import join, dirname, abspath
from unittest import TestCase
from unittest.mock import Mock
from pysplit.config import ServerConfig


class TestConfig(TestCase):
    def setUp(self):
        self.cfg = ServerConfig()
        self.cfg._cmd_args = Mock(
            config=join(dirname(dirname(abspath(__file__))), 'example_pysplit.yaml'),
            record_db='a_sqlite_file'
        )

    def test_configure(self):
        self.cfg.configure()
        self.assertEqual(self.cfg['record_db'], 'a_sqlite_file')
