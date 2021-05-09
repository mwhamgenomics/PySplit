from tests import TestPySplit
from pysplit.config import cfg


class TestConfig(TestPySplit):
    def test_config(self):
        self.assertEqual(cfg['server']['port'], 5000)

    def test_resolve_split_names(self):
        self.assertDictEqual(
            {
                'a_speedrun': ['level_1', 'level_2', 'level_3'],
                'another_run': ['level_1', 'level_2', 'level_3']
            },
            cfg['client']['split_names']
        )

    def test_query_dict(self):
        self.assertEqual(cfg.query('client', 'controls', 'advance'), 32)
        self.assertEqual(cfg.query('client', 'split_names', 'a_speedrun'), ['level_1', 'level_2', 'level_3'])
        self.assertEqual(cfg.query('client', 'nonexistent', ret_default='things'), 'things')
