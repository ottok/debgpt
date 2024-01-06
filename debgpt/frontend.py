# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import os
import json
import rich
import uuid
import sys
from . import defaults
console = rich.get_console()


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
    '''
    The frontend instance holds the whole chat session. The context is the whole
    session for the next LLM query. Historical chats is also a part of the
    context for following up questions. You may feel LLMs smart when they
    get information from the historical chat in the same session.
    '''

    NAME = 'AbstractFrontend'

    def __init__(self, args):
        self.uuid = uuid.uuid4()
        self.session = []
        self.debgpt_home = args.debgpt_home
        console.log(f'{self.NAME}> Starting conversation {self.uuid}')

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
        fpath = os.path.join(self.debgpt_home, str(self.uuid) + '.json')
        with open(fpath, 'wt') as f:
            json.dump(self.session, f, indent=2)
        console.log(f'{self.NAME}> Conversation saved at {fpath}')


class OpenAIFrontend(AbstractFrontend):
    '''
    https://platform.openai.com/docs/quickstart?context=python
    '''
    NAME : str = 'OpenAIFrontend'
    debug : bool = False
    stream : bool = True
    system_message : str = defaults.OPENAI_SYSTEM_MESSAGE

    def __init__(self, args):
        super().__init__(args)
        from openai import OpenAI
        self.client = OpenAI(api_key=args.openai_api_key, base_url=args.openai_base_url)
        self.session.append({"role": "system", "content": self.system_message})
        self.model = args.openai_model
        self.kwargs = {'temperature': args.temperature, 'top_p': args.top_p}
        console.log(f'{self.NAME}> model={repr(self.model)}, '
                    + f'temperature={args.temperature}, top_p={args.top_p}.')

    def query(self, messages: Union[List, Dict, str]) -> list:
        # add the message into the session
        self.update_session(messages)
        if self.debug:
            console.log('send:', self.session[-1])
        completion = self.client.chat.completions.create(
            model=self.model, messages=self.session, stream=self.stream,
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
    ZMQ frontend communicates with a self-hosted ZMQ backend.
    '''
    NAME = 'ZMQFrontend'
    debug: bool = False
    stream: bool = False

    def __init__(self, args):
        import zmq
        super().__init__(args)
        self.zmq_backend = args.zmq_backend
        self.socket = zmq.Context().socket(zmq.REQ)
        self.socket.connect(self.zmq_backend)
        console.log(f'{self.NAME}> Connected to ZMQ backend {self.zmq_backend}.')
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
    ag.add_argument('--zmq_backend', '-B', default='tcp://localhost:11177')
    ag.add_argument('--frontend', '-F', default='zmq',
                    choices=('zmq', 'openai'))
    ag.add_argument('--debgpt_home', default=os.path.expanduser('~/.debgpt'))
    ag = ag.parse_args()
    console.print(ag)

    frontend = create_frontend(ag)
    f = frontend
    import IPython
    IPython.embed(colors='neutral')
