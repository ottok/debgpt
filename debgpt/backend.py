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
from rich.status import Status
from typing import List, Dict
import argparse
import zmq
from . import llm
import rich
import torch as th
console = rich.get_console()


class AbstractBackend:
    def __init__(self, args):
        self.llm = llm.create_llm(args)

    def listen(self, args):
        raise NotImplementedError

    def server(self):
        raise NotImplementedError


def stat_messages(messages: List[Dict], llm):
    context_size = llm.tok.apply_chat_template(messages, tokenize=True,
                                               return_tensors='pt').size(1)
    ret = f'num_msgs={len(messages)}, ctx_size={context_size}; '
    ret += f'latest={messages[-1]}'
    return ret


class ZMQBackend(AbstractBackend):
    def __init__(self, args):
        super().__init__(args)
        self.socket = zmq.Context().socket(zmq.REP)
        binduri = args.host + ':' + str(args.port)
        self.socket.bind(binduri)
        console.log(f'ZMQBackend> bind URI {binduri}. Ready to serve.')

    def listen(self):
        while True:
            msg = self.socket.recv_json()
            yield msg

    def server(self):
        for query in self.listen():
            console.log(
                f'ZMQBackend> recv query: {stat_messages(query, self.llm)}', markup=False)
            with Status('LLM Calculating ...', spinner='line'):
                reply = self.llm(query)
            console.log(
                f'ZMQBackend> send reply: {stat_messages(reply, self.llm)}', markup=False)
            msg_json = zmq.utils.jsonapi.dumps(reply)
            self.socket.send(msg_json)


def create_backend(args):
    if args.backend_impl == 'zmq':
        backend = ZMQBackend(args)
    else:
        raise NotImplementedError(args.backend_impl)
    return backend


if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument('--port', '-p', type=int, default=11177,
                    help='"11177" looks like "LLM"')
    ag.add_argument('--host', type=str, default='tcp://*')
    ag.add_argument('--backend_impl', type=str,
                    default='zmq', choices=('zmq',))
    ag.add_argument('--max_new_tokens', type=int, default=512)
    ag.add_argument('--llm', type=str, default='Mistral7B')
    ag.add_argument('--device', type=str,
                    default='cuda' if th.cuda.is_available() else 'cpu')
    ag.add_argument('--precision', type=str,
                    default='fp16' if th.cuda.is_available() else '4bit')
    ag = ag.parse_args()
    console.log(ag)

    backend = create_backend(ag)
    try:
        backend.server()
    except KeyboardInterrupt:
        pass
    console.log('Server shut down.')
