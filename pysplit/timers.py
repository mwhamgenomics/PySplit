import datetime
import threading
from time import sleep
from pysplit.records import Split


def now():
    return datetime.datetime.now()


class SimpleTimer(threading.Thread):
    header = 'Time        Split'

    def __init__(self, name, split_config):
        super().__init__()
        self.name = name
        self.splits = self._get_splits(split_config)
        self.split_idx = 0
        self.total_time = None
        self.start_time = None
        self.done = False
        self.level_offset = max(len(s.name) for s in self.splits)

    def run(self):
        max_width = self.level_offset + len(self.header)
        print('_' * max_width)
        if len(self.name) < max_width:
            ndashes = int((max_width - len(self.name) - 2) / 2)
            print('-' * ndashes + ' ' + self.name + ' ' + '-' * ndashes)
        else:
            print(self.name)

        self.start_time = now()
        self.current_split.start_time = now()

        print('Started at %s' % str(self.start_time)[:-7])
        print(' ' * self.level_offset + '  ' + self.header)
        while not self.done:
            self.render_current_time()
            sleep(0.001)

        self.total_time = self.time_since(self.start_time)
        print('Total  ' + ' ' * (self.level_offset - 5) + self.total_time)
        print(self.splits)

    @staticmethod
    def time_since(t):
        diff = now() - t
        return str(diff)[:10]

    def _get_splits(self, split_config):
        names = split_config  # if type(split_config) in (list, tuple) else config[self.name] TODO: add name config
        return [Split(self.name, n, names.index(n) + 1) for n in names]

    @property
    def current_split(self):
        return self.splits[self.split_idx]

    @property
    def last_split_end(self):
        if self.split_idx > 0:
            return self.splits[self.split_idx - 1].end_time
        return self.start_time

    def split(self):
        assert self.current_split.start_time
        _now = now()
        self.current_split.end_time = _now

        if self.split_idx + 1 >= len(self.splits):
            self.done = True
        else:
            self.split_idx += 1
            self.current_split.start_time = _now

    def render_current_time(self):
        print(
            '%s  %s  %s' % (
                self.current_split.name + ' ' * (self.level_offset - len(self.current_split.name)),
                self.time_since(self.splits[0].start_time),
                self.time_since(self.last_split_end)
            ),
            end='\r'
        )


styles = {
    'fg_black': '\033[30m',
    'fg_red': '\033[31m',
    'fg_green': '\033[32m',
    'fg_orange': '\033[33m',
    'fg_blue': '\033[34m',
    'fg_purple': '\033[35m',
    'fg_cyan': '\033[36m',
    'fg_light_grey': '\033[37m',
    'fg_dark_grey': '\033[90m',
    'fg_light_red': '\033[91m',
    'fg_light_green': '\033[92m',
    'fg_yellow': '\033[93m',
    'fg_light_blue': '\033[94m',
    'fg_pink': '\033[95m',
    'fg_light_cyan': '\033[96m'
}


# for k, v in styles.items():
#     print('\033[0m%s%s\033[0m' % (v, k))


def main():
    s = SimpleTimer('a speedrun', ('split_1', 'split_2'))
    s.start()
    for _ in s.splits:
        input()
        s.split()

    s.join()


if __name__ == '__main__':
    main()
