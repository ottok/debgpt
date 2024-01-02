# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import zmq
import json
import rich
console = rich.get_console()


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
    def __init__(self, args):
        super().__init__(args)
        self.socket = zmq.Context().socket(zmq.REQ)
        self.socket.connect(self.backend)
        console.log(f'ZMQFrontend> connected to {self.backend}')
        self.session = []

    def query(self, content: str) -> list:
        self.session.append({'role': 'user', 'content': content})
        msg_json = json.dumps(self.session)
        print('send:', msg_json)
        self.socket.send_string(msg_json)
        msg = self.socket.recv()
        self.session, reply = json.loads(msg)
        print('recv:', reply)
        return reply


if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument('--backend', '-B', default='tcp://localhost:11177')
    ag = ag.parse_args()
    console.print(ag)

    frontend = ZMQFrontend(ag)
    f = frontend
    import IPython
    IPython.embed(colors='neutral')
