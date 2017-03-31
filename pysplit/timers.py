import datetime
import threading
import yaml
from time import sleep
from os.path import expanduser, isfile
from pysplit import records


level_names = {}
cfg = expanduser('~/.pysplit.yaml')
if isfile(cfg):
    level_names = yaml.safe_load(open(cfg, 'r'))


def now():
    return datetime.datetime.now()


class SimpleTimer(threading.Thread):
    header = 'Time        Split'
    colours = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'orange': '\033[33m',
        'blue': '\033[34m',
        'purple': '\033[35m',
        'cyan': '\033[36m',
        'light_grey': '\033[37m',
        'dark_grey': '\033[90m',
        'light_red': '\033[91m',
        'light_green': '\033[92m',
        'yellow': '\033[93m',
        'light_blue': '\033[94m',
        'pink': '\033[95m',
        'light_cyan': '\033[96m',
        None: '\033[0m'
    }

    def __init__(self, name, split_config, colour=True):
        super().__init__()
        self.name = name
        self.splits = self._get_splits(split_config)
        self.split_idx = 0
        self.total_time = None
        self.start_time = None
        self.done = False
        self.level_offset = max(len(s.name) for s in self.splits)
        self.max_width = self.level_offset + len(self.header)
        self.colour = colour

    def run(self):
        print('_' * self.max_width)
        if len(self.name) < self.max_width:
            ndashes = int((self.max_width - len(self.name) - 2) / 2)
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

        self.report_total_time()

    def report_total_time(self):
        self.total_time = now() - self.start_time
        print('Total  ' + ' ' * (self.level_offset - 5) + self.render_timedelta(self.total_time))

    def render_timedelta(self, timedelta, colour=None):
        """
        Format a timedelta as, e.g, '01:30:25.50' or '-00:03:43.24'
        :param datetime.timedelta timedelta:
        :param str colour: a value from self.colours
        """
        if timedelta is None:
            return ''

        float_secs = (86400 * timedelta.days) + timedelta.seconds + (timedelta.microseconds / 1000000)
        if float_secs < 0:
            float_secs *= -1
            sign = '-'
        else:
            sign = ''

        mins, sec = divmod(float_secs, 60)
        hrs, mins = divmod(mins, 60)
        sec, usec = divmod(sec, 1)
        usec *= 100

        return self.render_text('%s%d:%02d:%02d.%02d' % (sign, hrs, mins, sec, usec), colour)

    def _get_splits(self, split_config):
        names = split_config if type(split_config) in (list, tuple) else level_names[self.name]
        return [records.Split(self.name, names.index(n) + 1, split_name=n) for n in names]

    @property
    def current_split(self):
        return self.splits[self.split_idx]

    @property
    def last_split_end(self):
        if self.split_idx > 0:
            return self.splits[self.split_idx - 1].end_time
        return self.start_time

    def split(self):
        self.render_current_time()
        assert self.current_split.start_time
        _now = now()
        self.current_split.end_time = _now

        if self.split_idx + 1 >= len(self.splits):
            self.done = True
        else:
            self.split_idx += 1
            self.current_split.start_time = _now

    def render_current_time(self):
        _now = now()
        print(
            '%s  %s  %s' % (
                self.current_split.name + ' ' * (self.level_offset - len(self.current_split.name)),
                self.render_timedelta(_now - self.splits[0].start_time),
                self.render_timedelta(_now - self.last_split_end)
            ),
            end='\r'
        )

    def render_text(self, text, colour):
        if self.colour and colour:
            return self.colours[None] + colour + text + self.colours[None]
        return text


class PBTimer(SimpleTimer):
    header = SimpleTimer.header + '       Comparison   PersonalBest'

    def __init__(self, name, split_config, colour=True):
        super().__init__(name, split_config, colour)
        self.pb = records.get_best_run(name)
        if not self.pb:
            self.pb = records.SpeedRun(name, splits=self.splits)

    @property
    def current_pb_split(self):
        return self.pb.splits[self.split_idx]

    def render_current_split_comparison(self):
        if self.current_pb_split.time_elapsed is None:
            return ''

        best_possible_end = self.current_split.start_time + self.current_pb_split.time_elapsed
        return self.render_comparison(now() - best_possible_end)

    def render_comparison(self, timedelta):
        """
        Format a timedelta as, e.g, '+01:30:25.50' or '-00:03:43.24'. Will be coloured red if + and green if -.
        :param datetime.timedelta timedelta:
        """
        float_secs = (86400 * timedelta.days) + timedelta.seconds + (timedelta.microseconds / 1000000)
        if float_secs < 0:
            float_secs *= -1
            sign = '-'
            colour = self.colours['light_green']
        else:
            sign = '+'
            colour = self.colours['red']

        mins, sec = divmod(float_secs, 60)
        hrs, mins = divmod(mins, 60)
        sec, usec = divmod(sec, 1)
        usec *= 100
        return self.render_text('%s%d:%02d:%02d.%02d' % (sign, hrs, mins, sec, usec), colour)

    def render_current_time(self):
        _now = now()
        print(
            '%s  %s  %s  %s  %s' % (
                self.current_split.name + ' ' * (self.level_offset - len(self.current_split.name)),
                self.render_timedelta(_now - self.splits[0].start_time),
                self.render_timedelta(_now - self.last_split_end),
                self.render_current_split_comparison(),
                self.render_timedelta(self.current_pb_split.time_elapsed)
            ),
            end='\r'
        )

    def report_total_time(self):
        self.total_time = now() - self.start_time
        report = 'Total  ' + ' ' * (self.level_offset - 5) + self.render_timedelta(self.total_time)
        report += ' ' * 14 + self.render_comparison(self.total_time - self.pb.total_time)
        report += '  ' + self.render_timedelta(self.pb.total_time)
        print(report)

    def join(self, timeout=None):
        super().join(timeout)
        s = records.SpeedRun(self.name, records.generate_id('runs'), splits=self.splits)
        s.push()
