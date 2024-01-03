# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from prompt_toolkit.styles import Style
from rich.markup import escape
from rich.status import Status
from rich.panel import Panel
from prompt_toolkit import prompt
import argparse
import os
import sys
from . import frontend
from . import debian
from . import defaults
import torch as th
import rich
console = rich.get_console()

__list_of_tasks__ = ('none', 'backend', 'ml', 'bts', 'buildd', 'file',
                     'vote', 'policy', 'devref', 'man', 'dev', 'x')


def parse_args(task, argv):
    '''
    this non-standard subparser implementation requires me to write much
    less code compared to the standard one.
    '''
    conf = defaults.Config()
    ag = argparse.ArgumentParser(f'debgpt {task}')
    ag.add_argument('--backend', '-B', type=str, default=conf['backend'])
    ag.add_argument('--debgpt_home', type=str, default=conf['debgpt_home'])
    ag.add_argument('--frontend', '-F', type=str, default=conf['frontend'], choices=('zmq', 'openai'))
    ag.add_argument('--interactive', '-i', action='store_true',
                    help='keep chatting with LLM. do not quit after the first reply.')
    ag.add_argument('--stream', '-S', type=bool, default=conf['stream'],
                    help='default to streaming mode when openai frontend is used')
    ag.add_argument('--openai_model_id', type=str, default=conf['oepnai_model_id'])
    if task == 'backend':
        # special mode for backend server.
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
    elif task == 'none':
        # None. Just talk with llm without context.
        pass
    elif task == 'stdin':
        # read stdin. special mode. no actions to be specified.
        pass
    elif task == 'ml':
        # mailing list
        ag.add_argument('--url', '-u', type=str, required=True)
        ag.add_argument('--raw', action='store_true', help='use raw html')
        ag.add_argument('action', type=str,
                        choices=debian.mailing_list_actions)
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
    elif task == 'vote':
        # vote.debian.org
        ag.add_argument('--suffix', '-s', type=str, required=True,
                        help='for example, 2023/vote_002')
        ag.add_argument('action', type=str, choices=debian.vote_actions)
    elif task == 'policy':
        # policy document (plain text)
        ag.add_argument('--section', '-s', type=str, required=True)
        ag.add_argument('action', type=str, choices=debian.policy_actions)
    elif task == 'devref':
        # devref document
        ag.add_argument('--section', '-s', type=str, required=True)
        ag.add_argument('action', type=str, choices=debian.devref_actions)
    elif task == 'man':
        # manual page
        ag.add_argument('--man', '-m', type=str, required=True)
        ag.add_argument('action', type=str, choices=debian.man_actions)
    elif task in ('dev', 'x'):
        # code editing with context
        ag.add_argument('--file', '-f', type=str, required=True,
                        help='path to file you want to edit')
        ag.add_argument('--policy', type=str, default=None,
                        help='which section of policy to look at?')
        ag.add_argument('action', type=str, choices=debian.dev_actions)
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
    if not os.path.exists(ag.debgpt_home):
        os.mkdir(ag.debgpt_home)

    # create frontend / backend depending on task
    if argv[1] == 'backend':
        from . import backend
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
    elif argv[1] == 'vote':
        msg = debian.vote(ag.suffix, ag.action)
    elif argv[1] == 'policy':
        msg = debian.policy(ag.section, ag.action)
    elif argv[1] == 'devref':
        msg = debian.devref(ag.section, ag.action)
    elif argv[1] == 'man':
        msg = debian.man(ag.man, ag.action)
    elif argv[1] in ('dev', 'x'):
        msg = debian.dev(ag.file, ag.action, policy=ag.policy,
                         debgpt_home=ag.debgpt_home)
    elif argv[1] == 'stdin':
        msg = debian.stdin()
    else:
        raise NotImplementedError

    # print the prompt and do the first query, if specified
    if msg is not None:
        console.print(Panel(escape(msg), title='Initial Prompt'))

        # query the backend
        if ag.stream:
            console.print(
                f'[bold green]LLM [{1+len(f.session)}]>[/bold green] ', end='')
            reply = f(msg)
        else:
            with Status('LLM', spinner='line'):
                reply = f(msg)
            console.print(Panel(escape(reply), title='LLM Reply'))
        # console.print('LLM>', reply)

    # drop the user into interactive mode if specified (-i)
    if ag.interactive:
        # create prompt_toolkit style
        prompt_style = Style(
            [('prompt', 'bold fg:ansibrightcyan'), ('', 'bold ansiwhite')])
        try:
            while text := prompt(f'{os.getlogin()} [{len(f.session)}]> ', style=prompt_style):
                if ag.stream:
                    console.print(
                        f'[bold green]LLM [{1+len(f.session)}]>[/bold green] ', end='')
                    reply = f(text)
                else:
                    with Status('LLM', spinner='line'):
                        reply = f(text)
                    console.print(Panel(escape(reply), title='LLM Reply'))
                # console.print('LLM>', reply)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass

    # dump session to json
    f.dump()

    # some notifications
    if argv[1] in ('vote',):
        # sensitive category
        console.print(Panel('''[bold white on red]LLM may hallucinate and generate incorrect contents. Please further judge the correctness of the information, and do not let LLM mislead your decision on sensitive tasks, such as debian voting.[/bold white on red]''', title='!!! Warning !!!'))
    else:
        console.print(Panel(
            '''[green]LLM may hallucinate and generate incorrect contents. Please further judge the correctness of the information[/green]''', title='Note'))


if __name__ == '__main__':
    main()
