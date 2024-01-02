# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import argparse
import zmq
from . import llm
import rich
console = rich.get_console()


class AbstractBackend:
    def __init__(self, args):
        self.llm = llm.create_llm(args)

    def listen(self, args):
        raise NotImplementedError

    def server(self):
        raise NotImplementedError


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
            console.log(f'ZMQBackend> received query: {query}')
            reply = self.llm(query)
            console.log(f'ZMQBackend> sending reply: {reply}', markup=False)
            msg_json = zmq.utils.jsonapi.dumps(reply)
            self.socket.send(msg_json)


def create_backend(args):
    if args.backend == 'zmq':
        backend = ZMQBackend(args)
    else:
        raise NotImplementedError(args.backend)
    return backend


if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    ag.add_argument('--port', '-p', type=int, default=11177, help='"11177" looks like "LLM"')
    ag.add_argument('--host', type=str, default='tcp://*')
    ag.add_argument('--backend', type=str, default='zmq', choices=('zmq',))
    ag.add_argument('--max_new_tokens', type=int, default=512)
    ag.add_argument('--llm', type=str, default='Mistral7B')
    ag = ag.parse_args()
    console.log(ag)

    backend = create_backend(ag)
    try:
        backend.server()
    except KeyboardInterrupt:
        pass
    console.log('Server shut down.')
