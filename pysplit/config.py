import yaml
import argparse
from yaml.parser import ParserError
from os.path import expanduser, isfile


class PySplitConfigError(Exception):
    pass


def query_dict(d, query_string, ret_default=None):
    result = d.copy()
    for q in query_string.split('.'):
        result = result.get(q)
        if result is None:
            return ret_default

    return result or ret_default


class Config:
    _cmd_args = None
    _file_cfg = None
    content = None

    def __init__(self):
        self.argparser = argparse.ArgumentParser()

    @property
    def cmd_args(self):
        if self._cmd_args is None:
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
                    try:
                        self._file_cfg = yaml.safe_load(f)
                    except ParserError:
                        raise PySplitConfigError('Config parsing error') from None
        return self._file_cfg

    def __getitem__(self, item):
        return self.content[item]

    def get(self, item, ret_default=None):
        return self.content.get(item, ret_default)

    def _add_args(self):
        self.argparser.add_argument('positional', help="Name of a run category, or 'server' to start a server")
        self.argparser.add_argument('--runner_name', help='Alternate gamer tag to run as')
        self.argparser.add_argument('--gold_sound', help='Sound file for gold splits')
        self.argparser.add_argument('--pb_sound', help='Sound file for PBs')
        self.argparser.add_argument('--server_url', help='URL to a PySplit server. Defaults to localhost:5000')
        self.argparser.add_argument('--ls', action='store_true', help='List all run categories')
        self.argparser.add_argument('--record_db', help='Server SQLite database. Defaults to ~/.pysplit.sqlite')
        self.argparser.add_argument('--port', type=int, default=5000, help='Port to run server on. Defaults to 5000')
        self.argparser.add_argument('--internal_server', action='store_true', help='Run a client and server at the same time.')
        self.argparser.add_argument('--config')

    def configure(self):
        self.content = {
            'positional': self.cmd_args.positional,
            'split_names': {n: self._resolve_split_names(n) for n in self.file_config['split_names']},
            'runner_name': self.cmd_args.runner_name or self.file_config['runner_name'],
            'gold_sound': self.cmd_args.gold_sound or self.file_config.get('gold_sound'),
            'pb_sound': self.cmd_args.pb_sound or self.file_config.get('pb_sound'),
            'server_url': self.cmd_args.server_url or self.file_config.get('server_url', 'http://localhost:5000'),
            'ls': self.cmd_args.ls,
            'controls': {
                'advance': query_dict(self.file_config, 'controls.advance', ret_default=32),  # space
                'stop_reset': query_dict(self.file_config, 'controls.stop_reset', ret_default=127),  # backspace
                'quit': query_dict(self.file_config, 'controls.quit', ret_default=113)  # q
            },
            'record_db': self.cmd_args.record_db or self.file_config.get('record_db', expanduser('~/.pysplit.sqlite')),
            'port': self.cmd_args.port or self.file_config.get('port', 5000),
            'internal_server': self.cmd_args.internal_server or self.file_config.get('internal_server', False)
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


cfg = Config()
