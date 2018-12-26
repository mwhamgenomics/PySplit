from os.path import join, dirname, abspath
from unittest import TestCase
from unittest.mock import Mock
from pysplit.config import Config, query_dict


class TestConfig(TestCase):
    def setUp(self):
        self.cfg = Config()
        self.cfg._cmd_args = Mock(
            config=join(dirname(dirname(abspath(__file__))), 'example_pysplit.yaml'),
            record_db='a_sqlite_file'
        )

    def test_configure(self):
        self.cfg.configure()
        self.assertEqual(self.cfg['record_db'], 'a_sqlite_file')

    def test_query_dict(self):
        d = {'this': {'that': 'other'}}
        self.assertEqual(query_dict(d, 'this.that'), 'other')
        self.assertEqual(query_dict(d, 'this'), {'that': 'other'})
        self.assertEqual(query_dict(d, 'another.more', ret_default='things'), 'things')
