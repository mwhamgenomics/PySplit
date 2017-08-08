from pysplit.timers import timer_map
from pysplit.config import cfg


def main():
    cfg.configure()
    s = timer_map[cfg['timer_type']](cfg)

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
