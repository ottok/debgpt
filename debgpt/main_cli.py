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
import rich
console = rich.get_console()

__list_of_tasks__ = ('none', 'ml', 'bts', 'file')


def parse_args(task, argv):
    '''
    this non-standard subparser implementation requires me to write much
    less code compared to the standard one.
    '''
    ag = argparse.ArgumentParser('DebGPT')
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
    elif task == 'ml':
        # mailing list
        ag.add_argument('--url', '-u', type=str, required=True)
        ag.add_argument('action', type=str, choices=('summary', 'reply'))
    elif task == 'bts':
        # bts
        ag.add_argument('--id', '-x', type=str, required=True)
        ag.add_argument('action', type=str, choices=('summary',))
    elif task == 'file':
        # ask questions regarding a specific file
        # e.g., license check (SPDX format), code improvement, code explain
        ag.add_argument('--file', '-f', type=str, required=True)
        ag.add_argument('action', type=str)
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

    # create frontend
    f = frontend.create_frontend(ag)

    # create task-specific prompts
    if argv[1] == 'none':
        msg = None
    elif argv[1] == 'ml':
        msg = debian.mailing_list(ag.url, ag.action)
    elif argv[1] == 'bts':
        msg = debian.bts(ag.id, ag.action)
    elif argv[1] == 'file':
        msg = debian.file(ag.file, ag.action)
    else:
        raise NotImplementedError

    # print the prompt and do the first query, if specified
    if msg is not None:
        console.print(Panel(msg, title='Initial Prompt'))

        # query the backend
        with Status('LLM Computing ...', spinner='line'):
            reply = f(msg)
        console.print(Panel(reply, title='LLM Reply'))
        # console.print('LLM>', reply)

    # drop the user into interactive mode if specified (-i)
    if ag.interactive:
        try:
            while text := prompt('Prompt> '):
                with Status('LLM Computing ...', spinner='line'):
                    reply = f(text)
                console.print(Panel(reply, title='LLM Reply'))
                # console.print('LLM>', reply)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass

    # dump session to json
    f.dump()


if __name__ == '__main__':
    main()
