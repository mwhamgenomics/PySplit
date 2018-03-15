from pysplit.client.curses_timer import CursesTimer
from pysplit.config import client_config as cfg


def main():
    cfg.configure()
    s = CursesTimer()
    s.run()
    return 0
