import sys
import curses
import signal
import datetime
import traceback
from time import sleep
from os.path import isfile
from threading import Thread
from subprocess import check_call
from pysplit.client import records
from pysplit.config import client_cfg as cfg


def now():
    return datetime.datetime.now()


class CursesTimer:
    state_loop = ('ready', 'running', 'done', 'stopped')

    def __init__(self):
        self.name = cfg['run_name']
        self._state = 'ready'
        self.descriptors = {}
        self.split_descriptors = []
        self.split_names = cfg['split_names'].get(self.name)
        if not self.split_names:
            raise records.PySplitClientError('No split names configured')

        self.longest_split_name = max(len(s) for s in self.split_names)
        self.gold_splits = []
        self.pb_splits = []
        self.split_idx = 0

        self.screen = None
        self.current_run = None
        self.pb_run = None
        self.active = True

        signal.signal(signal.SIGUSR1, self.advance)

    def init_runs_and_splits(self):
        self.current_run = records.Run({'name': self.name, 'runner': cfg['runner_name']})
        self.pb_run = records.get_pb_run(self.name, cfg['runner_name'])
        self.gold_splits = records.get_gold_splits(self.name)
        self.pb_splits = records.get_pb_splits(self.name, cfg['runner_name'])

        completed_run = records.request('get', 'runs', params={'order_by': '-end_time', 'name': self.name, 'max_results': 1})
        if completed_run:
            data = records.request('get', 'splits', params={'order_by': '-idx', 'run_id': self.name, 'max_results': 1})
            if data:
                max_idx = data[0]['idx']
                assert max_idx == len(self.split_names) - 1, '%s != %s' % (max_idx, len(self.split_names))

    def init_screen(self):
        self.screen = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, 8, curses.COLOR_BLACK)
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.nodelay(1)

    def end_screen(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()

    def set_state(self, state):
        self._state = state
        state += ' ' * (7 - len(state))
        self.descriptors['status'].thing = state
        self.descriptors['status'].render()

    def reset(self):
        self.init_runs_and_splits()
        self.screen.clear()
        self.split_idx = 0

        footer_offset = len(self.split_names) + 4  # 4 lines in the header
        record_time = records.get_best_run(self.name)
        completion_ratio = records.request('get', 'completion_ratio', params={'run_name': self.name})

        static_descriptors = (
            Descriptor(1, 0, self.name),
            Descriptor(2, 0, 'Completion ratio:'),
            Descriptor(3, 0, '_' * self.longest_split_name),
            Descriptor(3, self.longest_split_name + 2, 'Pace'),
            Descriptor(3, self.longest_split_name + 15, 'Time'),
            Descriptor(footer_offset, 0, '_' * self.longest_split_name),
            Descriptor(footer_offset + 1, 0, 'Total:'),
            Descriptor(footer_offset + 2, 0, 'PB:'),
            Descriptor(footer_offset + 3, 0, 'Sum of bests:'),
            Descriptor(footer_offset + 4, 0, 'Record is 0:00:00.00 by'),
            Descriptor(footer_offset + 6, 0, 'Status:'),
            Descriptor(footer_offset + 7, 0, 'Start/split: space'),
            Descriptor(footer_offset + 8, 0, 'Stop/reset: backspace')
        )

        self.descriptors = {
            'total_time': TimeDeltaDescriptor(footer_offset + 1, 7, datetime.timedelta()),
            'pb_time': TimeDeltaDescriptor(footer_offset + 2, 4, self.pb_run.elapsed_time if self.pb_run else None),
            'sum_of_bests_time': TimeDeltaDescriptor(footer_offset + 3, 14, sum([s.elapsed_time for s in self.gold_splits], datetime.timedelta())),
            'record_time': TimeDeltaDescriptor(footer_offset + 4, len('Record is '), record_time.elapsed_time if record_time else None),
            'record_holder': Descriptor(footer_offset + 4, len('Record is 0:00:00.00 by '), record_time.data.get('runner', 'unknown') if record_time else ''),
            'status': Descriptor(footer_offset + 6, 8, self._state),
            'completion_ratio': Descriptor(2, 18, '%s/%s' % (completion_ratio['completed'], completion_ratio['total']))
        }
        self.split_descriptors = [SplitDescriptor(4 + i, 0, self, i) for i in range(len(self.split_names))]

        for d in static_descriptors + tuple(self.descriptors.values()):
            d.add_screen(self.screen)
            d.render()

        self.set_state('ready')

    def start(self):
        _now = now()
        self.current_run.data['start_time'] = _now
        self.current_run.push()
        self.current_split.now = _now
        self.current_split.start()
        self.set_state('running')

    def stop(self):
        self.set_state('stopped')

    def split(self):
        _now = now()
        self.current_split.now = _now
        self.current_split.finish()

        if self.split_idx + 1 >= len(self.split_names):
            # finish
            self.set_state('done')
            self.current_run.data['end_time'] = _now
            total_time = _now - self.current_run.data['start_time']
            self.current_run.data['total_time'] = total_time.total_seconds()
            self.current_run.push()
            if self.pb_run and total_time > self.pb_run.elapsed_time:
                pass
            else:
                self.play_sound(cfg['pb_sound'])
        else:
            self.split_idx += 1
            self.current_split.now = _now
            self.current_split.start()

    def advance(self, sig=None, frame=None):
        if self._state == 'ready':
            self.start()
        elif self._state == 'running':
            self.split()

    def run(self):
        exit_status = 0
        try:
            self.init_screen()
            self.reset()

            while self.active:
                key = self.screen.getch()

                if key == 113:  # q
                    self.active = False
                elif key == 127:  # backspace
                    if self._state == 'running':
                        self.stop()
                    else:
                        self.reset()
                elif key == 32:  # space
                    self.advance()

                elif key < 0:  # no input
                    if self._state == 'running':
                        self.render_current_split()

                    sleep(0.01)

            self.end_screen()

        except (Exception, KeyboardInterrupt):
            exit_status = 1
            self.end_screen()
            etype, value, tb = sys.exc_info()
            stacktrace = ''.join(traceback.format_exception(etype, value, tb))
            print(stacktrace)

        finally:
            return exit_status

    def render_current_split(self):
        _now = now()
        self.current_split.now = _now
        self.current_split.render()
        self.descriptors['total_time'].thing = _now - self.current_run.data['start_time']
        self.descriptors['total_time'].render()

    @property
    def current_split(self):
        return self.split_descriptors[self.split_idx]

    def print(self, string):
        self.screen.addstr(0, 0, str(string))

    @staticmethod
    def play_sound(sound_file):
        if isfile(sound_file):
            t = Thread(target=check_call, args=(['afplay', sound_file],))
            t.start()


class Descriptor:
    def __init__(self, y, x, thing):
        self.y = y
        self.x = x
        self.thing = thing
        self.screen = None

    def render(self):
        self.screen.addstr(self.y, self.x, self.thing)

    def add_screen(self, scr):
        self.screen = scr


class TimeDeltaDescriptor(Descriptor):
    def render(self):
        self.render_timedelta(self.y, self.x, self.thing)

    def render_timedelta(self, y, x, timedelta, colour_pair=0):
        """Format a timedelta as, e.g, '01:30:25.50' or '-00:03:43.24'"""
        if timedelta is None:
            return

        t = (86400 * timedelta.days) + timedelta.seconds + (timedelta.microseconds / 1000000)
        mins, sec = divmod(t, 60)
        hrs, mins = divmod(mins, 60)
        sec, usec = divmod(sec, 1)
        usec *= 100

        self.screen.addstr(y, x, '%d:%02d:%02d.%02d' % (hrs, mins, sec, usec), curses.color_pair(colour_pair))


class SplitDescriptor(TimeDeltaDescriptor):
    def __init__(self, y, x, timer, idx):
        super().__init__(y, x, idx)
        self.now = self.split = self.pb_split = self.last_split_point = self.gold_split = None
        self.pb_pace = datetime.timedelta()

        self.timer = timer
        self.add_screen(timer.screen)
        self.screen.addstr(y, x, self.timer.split_names[idx])
        self.screen.addstr(y, self.timer.longest_split_name + 2, '--')

        if self.timer.pb_splits:
            self.pb_split = self.timer.pb_splits[idx]
            self.render_timedelta(
                y,
                self.timer.longest_split_name + 15,
                datetime.timedelta(seconds=self.pb_split.data['total_time']),
                4
            )
            self.pb_pace = datetime.timedelta()
            for s in self.timer.pb_splits[:idx + 1]:
                self.pb_pace += s.elapsed_time

        if idx < len(self.timer.gold_splits):
            self.gold_split = self.timer.gold_splits[idx]

    def _render_pb(self, total_time):
        """
        :param datetime.timedelta total_time:
        """
        self.render_timedelta(self.y, self.timer.longest_split_name + 15, total_time)

    def render(self):
        """Format a timedelta as, e.g, '01:30:25.50' or '-00:03:43.24'"""
        run_pace = self.now - self.timer.current_run.data['start_time']
        timedelta = run_pace - self.pb_pace

        t = (86400 * timedelta.days) + timedelta.seconds + (timedelta.microseconds / 1000000)
        if t < 0:
            t *= -1
            sign = '-'
            colour = 1
        else:
            sign = '+'
            colour = 2

        mins, sec = divmod(t, 60)
        hrs, mins = divmod(mins, 60)
        sec, usec = divmod(sec, 1)
        usec *= 100

        total_time = self.now - self.split.data['start_time']
        if self.gold_split and total_time > self.gold_split.elapsed_time:
            self.screen.addstr(
                self.y,
                self.timer.longest_split_name + 2,
                '%s%d:%02d:%02d.%02d' % (sign, hrs, mins, sec, usec),
                curses.color_pair(colour)
            )

    def start(self):
        self.split = records.Split(
            {'run_id': self.timer.current_run.data['id'], 'idx': self.thing, 'start_time': self.now}
        )
        self.split.push()

    def finish(self):
        """Like self.render, but with gold splits and split uploading"""
        run_pace = self.now - self.timer.current_run.data['start_time']
        timedelta = run_pace - self.pb_pace

        t = (86400 * timedelta.days) + timedelta.seconds + (timedelta.microseconds / 1000000)
        if t < 0:
            t *= -1
            sign = '-'
            colour = 1
        else:
            sign = '+'
            colour = 2

        mins, sec = divmod(t, 60)
        hrs, mins = divmod(mins, 60)
        sec, usec = divmod(sec, 1)
        usec *= 100

        total_time = self.now - self.split.data['start_time']
        if self.gold_split and total_time > self.gold_split.elapsed_time:
            pass
        else:
            self.timer.play_sound(cfg['gold_sound'])
            colour = 3

        self.screen.addstr(
            self.y,
            self.timer.longest_split_name + 2,
            '%s%d:%02d:%02d.%02d' % (sign, hrs, mins, sec, usec),
            curses.color_pair(colour)
        )

        self.render_timedelta(
            self.y,
            self.timer.longest_split_name + 15,
            total_time,
            0
        )

        self.split.data['end_time'] = self.now
        self.split.data['total_time'] = total_time.total_seconds()
        self.split.push()
