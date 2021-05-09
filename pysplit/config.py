import yaml


class PySplitConfigError(Exception):
    pass


class Config:
    def __init__(self):
        self.content = None

    def load(self, config_file):
        with open(config_file) as f:
            self.content = yaml.safe_load(f)

        self.content['client']['split_names'] = {
            run: self._resolve_split_names(run)
            for run in self.content['client']['split_names']
        }

    def __getitem__(self, item):
        return self.content[item]

    def get(self, item, ret_default=None):
        return self.content.get(item, ret_default)

    def query(self, *query, ret_default=None):
        result = self.content

        for q in query:
            result = result.get(q)
            if result is None:
                return ret_default

        return result

    def _resolve_split_names(self, run_name, splits_alias=None):
        splits = self.content['client']['split_names'][splits_alias or run_name]

        _type = type(splits)
        if _type in (list, tuple):
            return splits
        elif _type is str:
            return self._resolve_split_names(run_name, splits)
        else:
            raise TypeError('Bad type for split names: %s' % _type)


cfg = Config()
