import yaml
import argparse
from os.path import expanduser, isfile


class Config:
    _cmd_args = None
    _file_cfg = None
    content = None

    @property
    def cmd_args(self):
        if self._cmd_args is None:
            a = argparse.ArgumentParser()
            self._add_args(a)
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

    def _add_args(self, argparser):
        argparser.add_argument('--config')

    def configure(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self.content[item]

    def get(self, item, ret_default=None):
        return self.content.get(item, ret_default)


class ClientConfig(Config):
    def _add_args(self, argparser):
        super()._add_args(argparser)
        argparser.add_argument('speedrun_name')
        argparser.add_argument('--split_names', nargs='+', default=None)
        argparser.add_argument('--nocolour', action='store_true')
        argparser.add_argument('--runner_name')
        argparser.add_argument('--compare', help="Valid values: 'pb', 'wr', 'average', 'practice', or any run ID")

    def configure(self):
        cmd_args = self.cmd_args
        file_cfg = self.file_config
        speedrun_name = cmd_args.speedrun_name

        self.content = {
            'speedrun_name': speedrun_name,
            'nocolour': cmd_args.nocolour or file_cfg.get('nocolour', False),
            'compare': cmd_args.compare or file_cfg.get('compare', 'practice'),
            'runner_name': cmd_args.runner_name or file_cfg['runner_name']
        }


class ServerConfig(Config):
    def configure(self):
        self.content = {
            'split_names': {},
            'record_db': self.cmd_args.record_db or expanduser('~/.pysplit.sqlite')
        }
        for speedrun_name in self.file_config['split_names']:
            self.content['split_names'][speedrun_name] = self._resolve_split_names(speedrun_name)

    def _resolve_split_names(self, speedrun_name, splits_alias=None):
        splits = self.file_config['split_names'][splits_alias or speedrun_name]

        _type = type(splits)
        if _type in (list, tuple):
            return splits
        elif _type is str:
            return self._resolve_split_names(speedrun_name, splits)
        else:
            raise TypeError('Bad type for split names: %s' % _type)

    def _add_args(self, argparser):
        super()._add_args(argparser)
        argparser.add_argument('--record_db')


client_config = ClientConfig()
server_config = ServerConfig()
