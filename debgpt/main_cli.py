# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import argparse
import os
import sys
from . import frontend
from . import debian
import rich
console = rich.get_console()
from prompt_toolkit import prompt
from rich.panel import Panel

def get_parser():
    ag = argparse.ArgumentParser('DebGPT')
    ag.add_argument('--backend', '-B', type=str, default='tcp://localhost:11177')
    ag.add_argument('--debgpt_home', type=str, default=os.path.expanduser('~/.debgpt'))
    ag.add_argument('--frontend', '-F', type=str, default='zmq')
    ag.add_argument('--interactive', '-i', action='store_true', help='keep chatting with LLM instead of one-shot query')
    return ag


def subparser_ml(ag, argv):
    ag.add_argument('--url', '-u', type=str, required=True)
    ag.add_argument('--action', '-a', type=str, required=True, choices=('summary', 'reply'))
    ag = ag.parse_args(argv)
    return ag


def main():
    argv = sys.argv
    if len(argv) < 2:
        console.print('Please specify the task. Possible tasks are:')
        console.print([x.lstrip('subparser_') for x in globals().keys() if x.startswith('subparser')])
        exit()

    # misc. a little bit messy here
    ag = get_parser()
    if argv[1] == 'ml':
        ag = subparser_ml(ag, argv[2:])
        console.log(ag)
        # create frontend
        f = frontend.create_frontend(ag)
        # create prompt
        msg = debian.mailing_list(ag.url, ag.action)
    else:
        raise NotImplementedError
    console.print(Panel(msg, title='Initial Prompt'))

    # query the backend
    reply = f(msg)
    console.print(Panel(reply, title='LLM Reply'))
    #console.print('LLM>', reply)

    if ag.interactive:
        try:
            while text := prompt('Prompt> '):
                reply = f(text)
                console.print(Panel(reply, title='LLM Reply'))
                #console.print('LLM>', reply)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass

    # dump sessino to json
    f.dump()


if __name__ == '__main__':
    main()