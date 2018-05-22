from pysplit.client.curses_timer import CursesTimer
from pysplit.client.records import request
from pysplit.config import client_cfg


def main():
    client_cfg.configure()
    if client_cfg['ls']:
        api_runs = request('GET', 'run_categories')
        cfg_runs = list(client_cfg['split_names'])
        runs = sorted(set(api_runs + cfg_runs))
        for r in runs:
            print(r)
        return

    s = CursesTimer()
    s.run()
