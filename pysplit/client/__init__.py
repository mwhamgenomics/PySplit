from pysplit.client.timers import SimpleTimer, ComparisonTimer
from pysplit.config import client_config as cfg


def main():
    cfg.configure()
    if cfg['compare'] == 'practice':
        s = SimpleTimer()
    else:
        s = ComparisonTimer()

    s.start()
    try:
        for _ in s.splits:
            input()
            s.split()
    except (KeyboardInterrupt, EOFError):
        s.done = True  # break out of the timer's main loop...
        s.cancel = True  # ...and set a flag not to run finish()
    finally:
        s.join()

    return 0
