from pysplit.timers import SimpleTimer, PBTimer
from pysplit.config import cfg


def main():
    cfg.configure()
    cls = SimpleTimer if cfg['practice'] else PBTimer

    s = cls(cfg['speedrun_name'], cfg['split_names'], cfg['colour'])
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
