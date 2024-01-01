# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import argparse
import zmq
import rich
console = rich.get_console()


class AbstractBackend:
    def __init__(self, args):
        self.llm = lambda x: x

    def listen(self, args):
        pass


class ZMQBackend(AbstractBackend):
    def __init__(self, args):
        super().__init__(args)
        self.socket = zmq.Context().socket(zmq.REP)
        binduri = args.host + ':' + str(args.port)
        self.socket.bind(binduri)
        console.log(f'ZMQBackend> bind URI {binduri}')

    def listen(self):
        while True:
            msg = self.socket.recv_json()
            yield msg

    def server(self):
        for query in self.listen():
            console.log(f'ZMQBackend> processing query {query}')
            reply = self.llm(query)
            reply = zmq.utils.jsonapi.dumps(reply)
            self.socket.send(reply)


if __name__ == '__main__':
    ag = argparse.ArgumentParser()
    # "11177" looks like "llM"
    ag.add_argument('--port', '-p', type=int, default=11177)
    ag.add_argument('--host', type=str, default='tcp://*')
    ag.add_argument('--backend', type=str,
                    default='ZMQBackend', choices=('ZMQBackend',))
    ag = ag.parse_args()
    console.print(ag)

    backend = globals()[ag.backend](ag)
    backend.server()
