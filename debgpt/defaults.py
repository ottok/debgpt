# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import os
try:
    import tomllib  # requires python >= 3.10
except:
    import pip._vendor.tomli as tomllib  # for python < 3.10
import rich


########################
# Configuration handling
########################


HOME = os.path.expanduser('~/.debgpt')
CONFIG = os.path.join(HOME, 'config.toml')

class Config(object):
    def __init__(self, home: str = HOME, config: str = CONFIG):
        # default
        self.toml = {'backend': 'tcp://localhost:11177',
                     'debgpt_home': HOME,
                     'frontend': 'zmq',
                     'stream': True,
                     'openai_model': 'gpt-4',
                     'temperature': 0.5,
                     'top_p': 1.0,
                     }
        # the defaults will be overriden by config file
        if not os.path.exists(home):
            os.mkdir(home)
        if os.path.exists(config):
            with open(config, 'rb') as f:
                content = tomllib.load(f)
                self.toml.update(content)
        # the config file will be overriden by command line next
    def __getitem__(self, index):
        return self.toml.__getitem__(index)
    def __getattr__(self, index):
        return self.toml.__getitem__(index)

########################
# Question templates
########################

QUESTIONS = {
    ':none': '',
    ':free': 'Read the above information carefully, and I will ask you questions later. Be quiet for now.',
    ':brief': 'please briefly summarize the above information, with very short sentences.',
    ':summary': 'Please summarize the above information.',
    ':summary_table': 'Please summarize the above information. Make a table to organize it.',
    ':polish': 'Please polish the language in the above texts, while not changing their original meaning.',
    ':rephrase': 'Please rephrase the above texts, while not changing their original meaning.',
    ':git-commit': 'Use a very short sentence to describe the above `git diff` as a git commit message.',
    }


def print_question_templates():
    console = rich.get_console()
    console.print(QUESTIONS)
