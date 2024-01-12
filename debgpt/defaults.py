'''
MIT License

Copyright (c) 2024 Mo Zhou <lumin@debian.org>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
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
        # The built-in defaults will be overridden by config file
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
        # the built-in defaults will be overridden by config file
        if not os.path.exists(home):
            os.mkdir(home)
        if os.path.exists(config):
            with open(config, 'rb') as f:
                content = tomllib.load(f)
                self.toml.update(content)
        # some arguments will be overrden by environment variables
        if (openai_api_key := os.getenv('OPENAI_API_KEY', None)) is not None:
            self.toml.openai_api_key = openai_api_key
        # all the above will be overridden by command line arguments
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
    ':what': 'What is the purpose of the above material?',
    ':explain': 'Please explain the above information.',
    ':brief': 'please briefly summarize the above information, with very short sentences.',
    ':summary': 'Please summarize the above information.',
    ':summary_table': 'Please summarize the above information. Make a table to organize it.',
    ':polish': 'Please polish the language in the above texts, while not changing their original meaning.',
    ':rephrase': 'Please rephrase the above texts, while not changing their original meaning.',
    ':git-commit': 'Write a good git commit message subject line for the change diff shown above, using the project style visible in previous commits titles above.',
    ':licensecheck': 'What is the license of this file? Just tell me the SPDX identifier, and answer in the shortest format.',
    ':diff': 'Please explain the differences among the above choices.',
    ':diff_table': 'Please explain the differences among the above choices. Organize your answer in tabular format.',
}


def print_question_templates():
    console = rich.get_console()
    console.print(QUESTIONS)


FORTUNE_QUESTIONS = {
    ':any': 'Tell me anything in your mind.',
    ':random': 'Greet with me, and tell me anything in your mind. Note, NSFW content is forbidden.',
    ':fun': 'Greet with me, and tell me something that is funny.',
    ':math': 'Greet with me, and tell me something interesting about mathematics.',
    ':joke': 'Greet with me, and tell me a joke.',
    ':computer': 'Greet with me, and tell me something about computers.',
    ':art': 'Greet with me, and tell me something about art.',
    ':cook': 'Greet with me, and tell me something about cooking.',
    ':phi': 'Greet with me, and tell me something about philosophy.',
    ':poem': 'Greet with me, and write a beautiful poem for me.',
}


def print_fortune_question_templates():
    console = rich.get_console()
    console.print(FORTUNE_QUESTIONS)


########################
# System Messages
########################

OPENAI_SYSTEM_MESSAGE = '''\
You are an excellent free software developer. You write high-quality code.
You aim to provide people with prefessional and accurate information.
You cherrish software freedom. You obey the Debian Social Contract and the
Debian Free Software Guideline. You follow the Debian Policy.'''
