import datetime
import threading
from time import sleep
from pysplit import records
from pysplit.config import cfg


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
        'gold': '\033[93m',
        'light_blue': '\033[94m',
        'pink': '\033[95m',
        'light_cyan': '\033[96m',
        None: '\033[0m'
    }

    def __init__(self):
        super().__init__()
        self.name = cfg['speedrun_name']
        self.splits = self._get_splits(cfg['split_names'])
        self.split_idx = 0
        self.total_time = None
        self.start_time = None
        self.finish_time = None
        self.done = False
        self.cancel = None
        self.level_offset = max(len(s.name) for s in self.splits)
        self.max_width = self.level_offset + len(self.header)
        self.colour = not cfg['nocolour']

    def preamble(self):
        print('Started at %s' % str(self.start_time)[:-7])
        print(' ' * self.level_offset + '  ' + self.header)

    def run(self):
        if len(self.name) < self.max_width:
            ndashes = int((self.max_width - len(self.name) - 2) / 2)
            print('-' * ndashes + ' ' + self.name + ' ' + '-' * ndashes)
        else:
            print(self.name)

        self.start_time = now()
        self.current_split.start_time = now()

        self.preamble()
        while not self.done:
            self.render_current_time()
            sleep(0.001)

        self.finish_time = now()

    def join(self, timeout=None):
        super().join(timeout)
        if self.cancel:
            print('\nCancelled')
        else:
            self.finish()

    def finish(self):
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

    def _get_splits(self, split_names):
        return [records.Split(self.name, split_names.index(n) + 1, split_name=n) for n in split_names]

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
            '{name}  {time}  {split}'.format(
                name=self.current_split.name + ' ' * (self.level_offset - len(self.current_split.name)),
                time=self.render_timedelta(_now - self.splits[0].start_time),
                split=self.render_timedelta(_now - self.last_split_end)
            ),
            end='\r'
        )

    def render_text(self, text, colour):
        if self.colour and colour:
            return self.colours[None] + colour + text + self.colours[None]
        return text


class ComparisonTimer(SimpleTimer):
    header = SimpleTimer.header + '       Compare'
    comp_aliases = {
        'pb': 'Personal best',
        'wr': 'World record',
        'average': 'Average'
    }

    def __init__(self):
        super().__init__()
        self.gold_splits = records.get_gold_splits(self.name)
        self.comp_run = self.get_comp_run()

    def get_comp_run(self):
        if cfg['compare'] == 'pb':
            return records.get_pb_run(self.name)
        elif cfg['compare'] == 'wr':
            return records.get_best_run(self.name)
        elif cfg['compare'] == 'average':
            return records.get_average_run(self.name)
        else:
            return records.get_run(self.name, cfg['compare'])

    @property
    def current_comp_split(self):
        return self.comp_run.splits[self.split_idx]

    @property
    def current_gold_split(self):
        return self.gold_splits[self.split_idx]

    def render_current_split_comparison(self):
        if self.comp_run is None:
            return ''

        _now = now()

        time_elapsed = _now - self.current_split.start_time

        if time_elapsed < self.current_comp_split.time_elapsed:
            colour = 'green'
        else:
            colour = 'red'

        comp_end = self.current_split.start_time + self.current_comp_split.time_elapsed
        comp = _now - comp_end
        return self.render_comparison(comp, colour)

    def render_comparison(self, timedelta, colour):
        """
        Format a timedelta as, e.g, '+01:30:25.50' or '-00:03:43.24'. Will be coloured red if + and green if -.
        :param datetime.timedelta timedelta:
        """
        t = timedelta.total_seconds()
        if t < 0:
            t *= -1
            sign = '-'
        else:
            sign = '+'

        mins, sec = divmod(t, 60)
        hrs, mins = divmod(mins, 60)
        sec, usec = divmod(sec, 1)
        usec *= 100
        return self.render_text('%s%d:%02d:%02d.%02d' % (sign, hrs, mins, sec, usec), self.colours[colour])

    def render_current_time(self):
        _now = now()
        print(
            '{name}{spaces}  {time}  {split}  {comp}'.format(
                name=self.current_split.name,
                spaces=' ' * (self.level_offset - len(self.current_split.name)),
                time=self.render_timedelta(_now - self.splits[0].start_time),
                split=self.render_timedelta(_now - self.last_split_end),
                comp=self.render_current_split_comparison()
            ),
            end='\r'
        )

    def preamble(self):
        print('Started at %s' % str(self.start_time)[:-7])

        if self.comp_run is None:
            if cfg['compare'] == 'pb':
                msg = 'Personal best is this run'
            else:
                msg = 'No compare run available'
        else:
            msg = '%s run is %s' % (self.comp_aliases[cfg['compare']], self.render_timedelta(self.comp_run.total_time))
            if self.comp_run.runner != cfg['runner_name']:
                msg += ' by %s' % self.comp_run.runner

            end = self.comp_run.splits[-1].end_time
            msg += ' from %s' % datetime.datetime(end.year, end.month, end.day, end.hour, end.minute, end.second)

        print(msg)
        print(' ' * self.level_offset + '  ' + self.header)

    def finish(self):
        self.total_time = now() - self.start_time
        msg = '{name}{spaces}  {time}  {split}'.format(
            name='Total',
            spaces=' ' * (self.level_offset - 5),
            time=self.render_timedelta(self.total_time),
            split=' ' * 10
        )
        if self.comp_run:
            diff = self.total_time - self.comp_run.total_time
            colour = 'green' if diff.total_seconds() < 0 else 'red'
            msg += '  {comp}'.format(comp=self.render_comparison(self.total_time - self.comp_run.total_time, colour))

        print(msg)
        s = records.SpeedRun(self.name, cfg['runner_name'], records.generate_id('runs'), splits=self.splits)
        s.push()
