import threading
from unittest import TestCase
from pysplit import server
from tests.data import speedruns


class TestPySplit(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=server.main, args=(':memory:',))
        cls.server_thread.start()
        for run in speedruns:
            run.push()

    @classmethod
    def tearDownClass(cls):
        server.stop()
        cls.server_thread.join()
