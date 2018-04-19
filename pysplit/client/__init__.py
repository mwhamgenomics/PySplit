from pysplit.client.curses_timer import CursesTimer
from pysplit.config import client_cfg


def main():
    client_cfg.configure()
    s = CursesTimer()
    s.run()
