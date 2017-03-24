import datetime
import threading
from time import sleep
from sys import stdout


def now():
    return datetime.datetime.now()


class SpeedRun(threading.Thread):
    def __init__(self, title, levels):
        super().__init__()
        self.title = title
        self.levels = levels
        self.start_time = None
        self.last_split = None
        self.current_level = self.levels[0]
        self.done = False
        self.level_offset = max(len(l) for l in self.levels)

    def run(self):
        max_width = self.level_offset + 24
        print('_' * max_width)
        if len(self.title) < max_width:
            ndashes = int((max_width - len(self.title) - 2) / 2)
            print('-' * ndashes + ' ' + self.title + ' ' + '-' * ndashes)
        else:
            print(self.title)
        print(' ' * self.level_offset + '  Time        Split')

        self.start_time = now()
        self.last_split = now()

        while not self.done:
            self.render_current_time()
            sleep(0.001)

        print('Total  ' + ' ' * (self.level_offset - 5) + self.time_since(self.start_time))

    @staticmethod
    def time_since(t):
        diff = now() - t
        return str(diff)[:10]

    def split(self):
        level_idx = self.levels.index(self.current_level)
        next_level_idx = level_idx + 1
        if next_level_idx >= len(self.levels):
            self.done = True
        else:
            self.current_level = self.levels[level_idx + 1]
            self.last_split = now()

    def render_current_time(self):
        stdout.write(
            '\r%s  %s  %s' % (
                self.current_level + ' ' * (self.level_offset - len(self.current_level)),
                self.time_since(self.start_time),
                self.time_since(self.last_split)
            )
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
    s = SpeedRun('a speedrun', ['level_1', 'level_2'])
    s.start()
    for _ in s.levels:
        input()
        s.split()

    s.join()


if __name__ == '__main__':
    main()
