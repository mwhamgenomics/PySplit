from pysplit.client.curses_timer import CursesTimer
from pysplit.client.records import request, PySplitClientError
from pysplit.config import cfg


def main():
    if cfg['positional'] == 'ls':
        try:
            api_runs = request('GET', 'run_categories')
        except PySplitClientError:
            api_runs = []

        cfg_runs = list(cfg['split_names'])
        runs = sorted(set(api_runs + cfg_runs))
        for r in runs:
            print(r)
        return

    s = CursesTimer()
    s.run()
