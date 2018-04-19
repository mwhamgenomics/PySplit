import yaml
import argparse
from os.path import expanduser, isfile


class Config:
    _cmd_args = None
    _file_cfg = None
    content = None

    def __init__(self):
        self.argparser = argparse.ArgumentParser()

    @property
    def cmd_args(self):
        if self._cmd_args is None:
            self.argparser.add_argument('--config')
            self._add_args()
            self._cmd_args = self.argparser.parse_args()
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

    def _add_args(self):
        pass

    def configure(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self.content[item]

    def get(self, item, ret_default=None):
        return self.content.get(item, ret_default)


class ClientConfig(Config):
    def _add_args(self):
        self.argparser.add_argument('run_name')
        self.argparser.add_argument('--runner_name')
        self.argparser.add_argument('--gold_sound')
        self.argparser.add_argument('--pb_sound')

    def configure(self):
        self.content = {
            'run_name': self.cmd_args.run_name,
            'split_names': {n: self._resolve_split_names(n) for n in self.file_config['split_names']},
            'runner_name': self.cmd_args.runner_name or self.file_config['runner_name'],
            'gold_sound': self.cmd_args.gold_sound or self.file_config.get('gold_sound'),
            'pb_sound': self.cmd_args.pb_sound or self.file_config.get('pb_sound')
        }

    def _resolve_split_names(self, run_name, splits_alias=None):
        splits = self.file_config['split_names'][splits_alias or run_name]

        _type = type(splits)
        if _type in (list, tuple):
            return splits
        elif _type is str:
            return self._resolve_split_names(run_name, splits)
        else:
            raise TypeError('Bad type for split names: %s' % _type)


class ServerConfig(Config):
    def configure(self):
        self.content = {
            'record_db': self.cmd_args.record_db or expanduser('~/.pysplit.sqlite')
        }

    def _add_args(self):
        self.argparser.add_argument('--record_db')


client_cfg = ClientConfig()
server_cfg = ServerConfig()
