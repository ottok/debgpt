# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import os
import json
import rich
import uuid
import sys
console = rich.get_console()
try:
    import tomllib  # requires python >= 3.10
except:
    import pip._vendor.tomli as tomllib  # for python < 3.10


def _check(messages: List[Dict]):
    '''
    communitation protocol.
    both huggingface transformers and openapi api use this
    '''
    assert isinstance(messages, list)
    assert all(isinstance(x, dict) for x in messages)
    assert all('role' in x.keys() for x in messages)
    assert all('content' in x.keys() for x in messages)
    assert all(isinstance(x['role'], str) for x in messages)
    assert all(isinstance(x['content'], str) for x in messages)
    assert all(x['role'] in ('system', 'user', 'assistant') for x in messages)


class AbstractFrontend():
    def __init__(self, args):
        self.backend = args.backend

    def query(self, messages):
        '''
        the messages format can be found in _check(...) function above.
        '''
        raise NotImplementedError

    def update_session(self, messages: Union[List, Dict, str]) -> None:
        if isinstance(messages, list):
            # reset the chat with provided message list
            self.session = messages
        elif isinstance(messages, dict):
            # just append a new dict
            self.session.append(messages)
        elif isinstance(messages, str):
            # just append a new user dict
            self.session.append({'role': 'user', 'content': messages})
        else:
            raise TypeError(type(messages))
        _check(self.session)

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    def dump(self):
        raise NotImplementedError


class OpenAIFrontend(AbstractFrontend):
    '''
    https://platform.openai.com/docs/quickstart?context=python
    '''
    NAME = 'OpenAIFrontend'
    debug = False
    model_id = "gpt-3.5-turbo"

    def __init__(self, args):
        super().__init__(args)
        from openai import OpenAI
        if (api_key := os.getenv('OPENAI_API_KEY', None)) is None:
            config_path = os.path.join(args.debgpt_home, 'config.toml')
            if os.path.exists(config_path):
                with open(config_path, 'rb') as f:
                    self.env = tomllib.load(f)
            else:
                raise FileNotFoundError(
                    f'Please put your OPENAI_API_KEY in environt variables or {config_path}')
            if 'OPENAI_API_KEY' not in self.env:
                raise KeyError(
                    f'the OPENAI_API_KEY is not found in environment variables, neither the config file {config_path}')
            api_key = self.env['OPENAI_API_KEY']
        self.client = OpenAI(api_key=api_key)
        self.uuid = uuid.uuid4()
        self.debgpt_home = args.debgpt_home
        self.session = []
        # self.session.append({"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."})
        self.session.append({"role": "system", "content": "You are an excellent free software developer. You write high-quality code. You aim to provide people with prefessional and accurate information. You cherrish software freedom. You obey the Debian Social Contract and the Debian Free Software Guideline. You follow the Debian Policy."})
        # streaming for fancy terminal effects
        self.stream = getattr(args, 'stream', False)
        # e.g., gpt-3.5-turbo, gpt-4
        self.model_id = getattr(args, 'openai_model_id', self.model_id)
        self.kwargs = {'temperature': args.temperature, 'top_p': args.top_p}
        console.log(f'{self.NAME}> instantiated with model={repr(self.model_id)}, stream={self.stream}, temperature={args.temperature}, top_p={args.top_p}')

    def dump(self):
        fpath = os.path.join(self.debgpt_home, str(self.uuid) + '.json')
        with open(fpath, 'wt') as f:
            json.dump(self.session, f, indent=2)
        console.log(f'{self.NAME}> LLM session saved at {fpath}')

    def query(self, messages: Union[List, Dict, str]) -> list:
        # add the message into the session
        self.update_session(messages)
        if self.debug:
            console.log('send:', self.session[-1])
        completion = self.client.chat.completions.create(
            model=self.model_id, messages=self.session, stream=self.stream,
            **self.kwargs)
        if self.stream:
            chunks = []
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    piece = chunk.choices[0].delta.content
                    chunks.append(piece)
                    print(piece, end="")
                    sys.stdout.flush()
            generated_text = ''.join(chunks)
            if not generated_text.endswith('\n'):
                print()
                sys.stdout.flush()
        else:
            generated_text = completion.choices[0].message.content
        new_message = {'role': 'assistant', 'content': generated_text}
        self.update_session(new_message)
        if self.debug:
            console.log('recv:', self.session[-1])
        return self.session[-1]['content']


class ZMQFrontend(AbstractFrontend):
    '''
    The frontend instance holds the whole chat session. The context is the whole session for the next LLM query.
    Historical chats is also a part of the context for following up questions.
    You may feel LLMs smart when they get information from the historical chat in the same session.
    '''
    NAME = 'ZMQFrontend'
    debug: bool = False

    def __init__(self, args):
        import zmq
        super().__init__(args)
        self.socket = zmq.Context().socket(zmq.REQ)
        self.socket.connect(self.backend)
        console.log(f'{self.NAME}> connected to {self.backend}')
        self.uuid = uuid.uuid4()
        console.log(f'{self.NAME}> started conversation {self.uuid}')
        self.debgpt_home = args.debgpt_home
        self.session = []
        #
        if hasattr(args, 'temperature'):
            console.log('warning! --temperature not yet supported for this frontend')
        if hasattr(args, 'top_p'):
            console.log('warning! --top_p not yet supported for this frontend')

    def query(self, content: Union[List, Dict, str]) -> list:
        if isinstance(content, list):
            self.session = content
        elif isinstance(content, dict):
            self.session.append(content)
        elif isinstance(content, str):
            self.session.append({'role': 'user', 'content': content})
        _check(self.session)
        msg_json = json.dumps(self.session)
        if self.debug:
            console.log('send:', msg_json)
        self.socket.send_string(msg_json)
        msg = self.socket.recv()
        self.session = json.loads(msg)
        _check(self.session)
        if self.debug:
            console.log('recv:', self.session[-1])
        return self.session[-1]['content']

    def dump(self):
        fpath = os.path.join(self.debgpt_home, str(self.uuid) + '.json')
        with open(fpath, 'wt') as f:
            json.dump(self.session, f, indent=2)
        console.log(f'ZMQFrontend> LLM session saved at {fpath}')


def create_frontend(args):
    if args.frontend == 'zmq':
        frontend = ZMQFrontend(args)
    elif args.frontend == 'openai':
        frontend = OpenAIFrontend(args)
    elif args.frontend == 'dryrun':
        frontend = None
    else:
        raise NotImplementedError
    return frontend


if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument('--backend', '-B', default='tcp://localhost:11177')
    ag.add_argument('--frontend', '-F', default='zmq',
                    choices=('zmq', 'openai'))
    ag.add_argument('--debgpt_home', default=os.path.expanduser('~/.debgpt'))
    ag = ag.parse_args()
    console.print(ag)

    frontend = create_frontend(ag)
    f = frontend
    import IPython
    IPython.embed(colors='neutral')
