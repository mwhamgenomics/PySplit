import os
import sys
import subprocess
from time import sleep
from signal import SIGINT
from pysplit.client.curses_timer import CursesTimer
from pysplit.client.records import request, PySplitClientError
from pysplit.config import cfg


def main(args):
    if cfg.query('client', 'server_url'):
        s = CursesTimer(args.name)
        s.run()

    else:  # standalone mode
        server_proc = subprocess.Popen(
            [sys.executable, __file__, 'server'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        sleep(0.1)
        s = CursesTimer(args.name)
        s.run()
        os.kill(server_proc.pid, SIGINT)
        server_proc.wait()


def list_runs(args):
    try:
        api_runs = request('GET', 'run_categories')
    except PySplitClientError:
        api_runs = []

    cfg_runs = list(cfg['client']['split_names'])
    runs = sorted(set(api_runs + cfg_runs))
    for r in runs:
        print(r)
