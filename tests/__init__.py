import os
from unittest import TestCase
from pysplit.config import cfg


class TestPySplit(TestCase):
    @classmethod
    def setUpClass(cls):
        cfg.load(os.path.join(os.path.dirname(__file__), '..', 'example_pysplit.yaml'))
