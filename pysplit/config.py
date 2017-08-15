import argparse
import yaml
from os.path import expanduser, isfile


class Config:
    _cmd_args = None
    _file_cfg = None
    content = None

    @property
    def cmd_args(self):
        if self._cmd_args is None:
            a = argparse.ArgumentParser()
            a.add_argument('speedrun_name')
            a.add_argument('--split_names', nargs='+', default=None)
            a.add_argument('--nocolour', dest='colour', action='store_false')
            a.add_argument('--timer_type')
            a.add_argument('--runner_name')
            a.add_argument('--config')
            a.add_argument('--compare', help='Compare with a specific run (only works with --timer_type specific)')
            self._cmd_args = a.parse_args()
        return self._cmd_args

    @property
    def file_config(self):
        if self._file_cfg is None:
            cfg_file = self.cmd_args.config or expanduser('~/.pysplit.yaml')
            self._file_cfg = {}
            if isfile(cfg_file):
                with open(cfg_file, 'r') as f:
                    self._file_cfg = yaml.safe_load(f)
        return self._file_cfg

    def configure(self):
        cmd_args = self.cmd_args
        file_cfg = self.file_config
        speedrun_name = cmd_args.speedrun_name

        self.content = {
            'speedrun_name': speedrun_name,
            'split_names': cmd_args.splits or self._resolve_split_names(speedrun_name),
            'nocolour': cmd_args.nocolour or file_cfg.get('nocolour', False),
            'timer_type': cmd_args.timer_type or file_cfg.get('timer_type', 'standard_timer'),
            'runner_name': cmd_args.runner_name or file_cfg['runner_name']
        }

    def _resolve_split_names(self, speedrun_name, splits_alias=None):
        splits = self.file_config['split_names'][splits_alias or speedrun_name]

        _type = type(splits)
        if _type in (list, tuple):
            return splits
        elif _type is str:
            return self._resolve_split_names(speedrun_name, splits)
        else:
            raise TypeError('Bad type for split names: %s' % _type)

    def __getitem__(self, item):
        return self.content[item]

    def get(self, item, ret_default=None):
        return self.content.get(item, ret_default)


cfg = Config()
