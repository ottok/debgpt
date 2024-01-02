# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from rich.status import Status
from rich.panel import Panel
from prompt_toolkit import prompt
import argparse
import os
import sys
from . import frontend
from . import debian
from . import backend
import rich
console = rich.get_console()
from rich.markup import escape

__list_of_tasks__ = ('none', 'ml', 'bts', 'file', 'buildd')


def parse_args(task, argv):
    '''
    this non-standard subparser implementation requires me to write much
    less code compared to the standard one.
    '''
    ag = argparse.ArgumentParser(f'debgpt {task}')
    ag.add_argument('--backend', '-B', type=str,
                    default='tcp://localhost:11177')
    ag.add_argument('--debgpt_home', type=str,
                    default=os.path.expanduser('~/.debgpt'))
    ag.add_argument('--frontend', '-F', type=str, default='zmq')
    ag.add_argument('--interactive', '-i', action='store_true',
                    help='keep chatting with LLM. do not quit after the first reply.')
    if task == 'none':
        # None. Just talk with llm without context.
        pass
    if task == 'backend':
        # special mode for backend server.
        ag.add_argument('--port', '-p', type=int, default=11177,
                        help='"11177" looks like "LLM"')
        ag.add_argument('--host', type=str, default='tcp://*')
        ag.add_argument('--backend_impl', type=str, default='zmq', choices=('zmq',))
        ag.add_argument('--max_new_tokens', type=int, default=512)
        ag.add_argument('--llm', type=str, default='Mistral7B')
    elif task == 'ml':
        # mailing list
        ag.add_argument('--url', '-u', type=str, required=True)
        ag.add_argument('--raw', action='store_true', help='use raw html')
        ag.add_argument('action', type=str, choices=debian.mailing_list_actions)
    elif task == 'bts':
        # bts
        ag.add_argument('--id', '-x', type=str, required=True)
        ag.add_argument('--raw', action='store_true', help='use raw html')
        ag.add_argument('action', type=str, choices=debian.bts_actions)
    elif task == 'buildd':
        # buildd
        ag.add_argument('--package', '-p', type=str, required=True)
        ag.add_argument('--suite', '-s', type=str, default='sid')
        ag.add_argument('--raw', action='store_true', help='use raw html')
        ag.add_argument('action', type=str, choices=debian.buildd_actions)
    elif task == 'file':
        # ask questions regarding a specific file
        # e.g., license check (SPDX format), code improvement, code explain
        # TODO: support multiple files (nargs=+)
        ag.add_argument('--file', '-f', type=str, required=True)
        ag.add_argument('action', type=str, choices=debian.file_actions)
    else:
        raise NotImplementedError(task)
    ag = ag.parse_args(argv)
    return ag


def main():
    # parse args
    argv = sys.argv
    if len(argv) < 2:
        console.print(
            'Please specify the task. Possible tasks are:', __list_of_tasks__)
        exit()
    ag = parse_args(argv[1], argv[2:])
    console.log(ag)

    # create frontend / backend depending on task
    if argv[1] == 'backend':
        b = backend.create_backend(ag)
        try:
            b.server()
        except KeyboardInterrupt:
            pass
        console.log('Server shut down.')
        exit(1)
    else:
        f = frontend.create_frontend(ag)

    # create task-specific prompts
    if argv[1] == 'none':
        msg = None
    elif argv[1] == 'ml':
        msg = debian.mailing_list(ag.url, ag.action, raw=ag.raw)
    elif argv[1] == 'bts':
        msg = debian.bts(ag.id, ag.action, raw=ag.raw)
    elif argv[1] == 'file':
        msg = debian.file(ag.file, ag.action)
    elif argv[1] == 'buildd':
        msg = debian.buildd(ag.package, ag.action, suite=ag.suite, raw=ag.raw)
    else:
        raise NotImplementedError

    # print the prompt and do the first query, if specified
    if msg is not None:
        console.print(Panel(escape(msg), title='Initial Prompt'))

        # query the backend
        with Status('LLM Computing ...', spinner='line'):
            reply = f(msg)
        console.print(Panel(escape(reply), title='LLM Reply'))
        # console.print('LLM>', reply)

    # drop the user into interactive mode if specified (-i)
    if ag.interactive:
        try:
            while text := prompt('Prompt> '):
                with Status('LLM Computing ...', spinner='line'):
                    reply = f(text)
                console.print(Panel(escape(reply), title='LLM Reply'))
                # console.print('LLM>', reply)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass

    # dump session to json
    f.dump()


if __name__ == '__main__':
    main()
