import argparse
from pysplit.timers import SimpleTimer, PBTimer


def main():
    a = argparse.ArgumentParser()
    a.add_argument('speedrun_name')
    a.add_argument('--splits', nargs='+', default=None)
    a.add_argument('--nocolour', dest='colour', action='store_false')
    a.add_argument('--practice', action='store_true')
    args = a.parse_args()

    cls = SimpleTimer if args.practice else PBTimer

    s = cls(args.speedrun_name, args.splits, args.colour)
    s.start()
    for _ in s.splits:
        input()
        s.split()

    s.join()
    return 0
