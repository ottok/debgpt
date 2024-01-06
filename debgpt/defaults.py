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
        # The built-in defaults will be overriden by config file
        self.toml = {
            # CLI/Frontend Bebavior
            'frontend': 'openai',
            'debgpt_home': HOME,
            # LLM Inference Parameters
            'temperature': 0.5,
            'top_p': 1.0,
            # OpenAI Frontend Specific
            'openai_base_url': 'https://api.openai.com/v1',
            'openai_model': 'gpt-3.5-turbo',
            'openai_api_key': 'empty',
            # ZMQ Frontend Specific
            'zmq_backend': 'tcp://localhost:11177',
        }
        # the built-in defaults will be overriden by config file
        if not os.path.exists(home):
            os.mkdir(home)
        if os.path.exists(config):
            with open(config, 'rb') as f:
                content = tomllib.load(f)
                self.toml.update(content)
        # some arguments will be overrden by environment variables
        if (openai_api_key := os.getenv('OPENAI_API_KEY', None)) is not None:
            self.toml.openai_api_key = openai_api_key
        # all the above will be overriden by command line arguments
        pass
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


########################
# System Messages 
########################

OPENAI_SYSTEM_MESSAGE = '''\
You are an excellent free software developer. You write high-quality code.
You aim to provide people with prefessional and accurate information.
You cherrish software freedom. You obey the Debian Social Contract and the
Debian Free Software Guideline. You follow the Debian Policy.'''
