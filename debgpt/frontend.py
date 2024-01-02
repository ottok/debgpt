# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import os
import zmq
import json
import rich
import uuid
console = rich.get_console()

def _check(messages: List[Dict]):
    assert isinstance(messages, list)
    assert all(isinstance(x, dict) for x in messages)
    assert all('role' in x.keys() for x in messages)
    assert all('content' in x.keys() for x in messages)
    assert all(isinstance(x['role'], str) for x in messages)
    assert all(isinstance(x['content'], str) for x in messages)


class AbstractFrontend():
    def __init__(self, args):
        self.backend = args.backend

    def query(self, content):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    def dump(self):
        raise NotImplementedError


class ZMQFrontend(AbstractFrontend):
    '''
    The frontend instance holds the whole chat session. The context is the whole session for the next LLM query.
    Historical chats is also a part of the context for following up questions.
    You may feel LLMs smart when they get information from the historical chat in the same session.
    '''
    debug : bool = False
    def __init__(self, args):
        super().__init__(args)
        self.socket = zmq.Context().socket(zmq.REQ)
        self.socket.connect(self.backend)
        console.log(f'ZMQFrontend> connected to {self.backend}')
        self.uuid = uuid.uuid4()
        console.log(f'ZMQFrontend> started conversation {self.uuid}')
        self.debgpt_home = args.debgpt_home
        self.session = []

    def query(self, content: str) -> list:
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
    else:
        raise NotImplementedError
    return frontend

if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument('--backend', '-B', default='tcp://localhost:11177')
    ag.add_argument('--frontend', '-F', default='zmq')
    ag.add_argument('--debgpt_home', default=os.path.expanduser('~/.debgpt'))
    ag = ag.parse_args()
    console.print(ag)

    frontend = ZMQFrontend(ag)
    f = frontend
    import IPython
    IPython.embed(colors='neutral')
