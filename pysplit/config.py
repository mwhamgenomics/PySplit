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
            a.add_argument('--splits', nargs='+', default=None)
            a.add_argument('--nocolour', dest='colour', action='store_false')
            a.add_argument('--practice', action='store_true')
            self._cmd_args = a.parse_args()
        return self._cmd_args

    @property
    def file_config(self):
        if self._file_cfg is None:
            cfg_file = expanduser('~/.pysplit.yaml')
            self._file_cfg = {}
            if isfile(cfg_file):
                self._file_cfg = yaml.safe_load(open(cfg_file, 'r'))
        return self._file_cfg

    def configure(self):
        cmd_args = self.cmd_args
        file_cfg = self.file_config
        speedrun_name = cmd_args.speedrun_name

        self.content = {
            'speedrun_name': speedrun_name,
            'split_names': cmd_args.splits or self._resolve_split_names(file_cfg['split_names'], speedrun_name),
            'colour': False if cmd_args.nocolour else file_cfg.get('nocolour', True),
            'practice': cmd_args.practice or file_cfg.get('practice', False)
        }

    @classmethod
    def _resolve_split_names(cls, level_names, speedrun_name):
        splits = level_names[speedrun_name]
        _type = type(splits)
        if _type in (list, tuple):
            return splits
        elif _type is str:
            return cls._resolve_split_names(splits, speedrun_name)
        else:
            raise TypeError('Bad type for split names: %s' % _type)

    def __getitem__(self, item):
        return self.content[item]

    def get(self, item):
        return self.content.get(item)


cfg = Config()
