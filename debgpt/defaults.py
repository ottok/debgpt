# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import os
try:
    import tomllib  # requires python >= 3.10
except:
    import pip._vendor.tomli as tomllib  # for python < 3.10

HOME = os.expanduser('~/.debgpt')
CONFIG = os.path.join(HOME, 'config.toml')

class Config(object):
    def __init__(self, home: str = HOME, config: str = CONFIG):
        # default
        self.toml = {'backend': 'tcp://localhost:11177',
                     'debgpt_home': HOME,
                     'frontend': 'zmq',
                     'stream': True,
                     'openai_model_id': 'gpt-4'
                     }
        # the defaults will be overriden by config file
        with open(config, 'rb') as f:
            self.toml.update(tomllib.load(f))
        # XXX: the config file will be overriden by command line
    def __getitem__(self, index):
        return self.toml.__getitem__(index)
