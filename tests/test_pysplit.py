import threading
from unittest import TestCase
from pysplit import server


class TestPySplit(TestCase):
    server_thread = None

    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=server.main, args=(':memory:',))
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        server.stop()
        cls.server_thread.join()
