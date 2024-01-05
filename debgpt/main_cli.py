# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.

# suppress all warnings.
import warnings
warnings.filterwarnings("ignore")

from typing import *
from prompt_toolkit.styles import Style
from rich.markup import escape
from rich.status import Status
from rich.panel import Panel
from prompt_toolkit import prompt, PromptSession
import argparse
import os
import sys
from . import frontend
from . import debian
from . import defaults
import rich
console = rich.get_console()


def task_backend(ag) -> None:
    from . import backend
    b = backend.create_backend(ag)
    try:
        b.server()
    except KeyboardInterrupt:
        pass
    console.log('Server shut down.')
    exit(0)

def task_replay(ag) -> None:
    from . import replay
    replay.replay(ag.json_file_path)
    exit(0)

def parse_args():
    '''
    argparse with subparsers
    '''
    conf = defaults.Config()
    ag = argparse.ArgumentParser()

    # LLM inference arguments
    ag.add_argument('--temperature', '-T', type=float, default=conf['temperature'])
    ag.add_argument('--top_p', '-P', type=float, default=conf['top_p'])

    # general frontend
    ag.add_argument('--debgpt_home', type=str, default=conf['debgpt_home'])
    ag.add_argument('--frontend', '-F', type=str, default=conf['frontend'], choices=('dryrun', 'zmq', 'openai'))

    # ZMQ frontend
    ag.add_argument('--backend', '-B', type=str, default=conf['backend'], help='the frontend endpoint')

    # openai frontend
    ag.add_argument('--openai_model_id', '-M', type=str, default=conf['openai_model_id'])

    # CLI behavior
    ag.add_argument('--quit', '-Q', action='store_true', help='directly quit after receiving the first response from LLM, instead of staying in interation.')
    ag.add_argument('--multiline', action='store_true', help='enable multi-line input for prompt_toolkit. use Meta+Enter to accept the input instead.')
    ag.add_argument('--hide_first_prompt', '-H', action='store_true', help='hide the first (generated) prompt; do not print argparse results')
    ag.add_argument('--verbose', '-v', action='store_true', help='verbose mode. helpful for debugging')
    ag.add_argument('--output', '-o', type=str, default=None, help='write the last LLM message to specified file') 

    # The following are task-specific subparsers
    subps = ag.add_subparsers(help='task help')
    ag.set_defaults(func=lambda ag: None)  # if no subparser specified

    # -- backend (special mode)
    ps_backend = subps.add_parser('backend', help='special mode: start backend server (self-hosted LLM inference)')
    ps_backend.add_argument('--port', '-p', type=int, default=11177,
                            help='"11177" looks like "LLM"')
    ps_backend.add_argument('--host', type=str, default='tcp://*')
    ps_backend.add_argument('--backend_impl', type=str,
                            default='zmq', choices=('zmq',))
    ps_backend.add_argument('--max_new_tokens', type=int, default=512)
    ps_backend.add_argument('--llm', type=str, default='Mistral7B')
    ps_backend.add_argument('--device', type=str, default='cuda')
    ps_backend.add_argument('--precision', type=str, default='fp16')
    ps_backend.set_defaults(func=task_backend)

    # -- none (special mode)
    # FIXME: deprecated.
    ps_none = subps.add_parser('none', help='degenerate into general chat without debian specific stuff')
    ps_none.set_defaults(func=lambda ag: None)

    # -- replay (special mode)
    ps_replay = subps.add_parser('replay', help='replay a conversation from a JSON file')
    ps_replay.add_argument('json_file_path', type=str, help='path to the JSON file')
    ps_replay.set_defaults(func=task_replay)

    # -- stdin
    ps_stdin = subps.add_parser('stdin', help='read stdin. special mode. no actions to be specified.')
    ps_stdin.set_defaults(func=lambda ag: debian.stdin())

    # -- mailing list
    ps_ml = subps.add_parser('ml', help='mailing list') 
    ps_ml.add_argument('--url', '-u', type=str, required=True)
    ps_ml.add_argument('--raw', action='store_true', help='use raw html')
    ps_ml.add_argument('action', type=str, choices=debian.mailing_list_actions)
    ps_ml.set_defaults(func=lambda ag: debian.mailing_list(ag.url, ag.action, raw=ag.raw))

    # --bts
    ps_bts = subps.add_parser('bts', help='BTS')
    ps_bts.add_argument('--id', '-x', type=str, required=True)
    ps_bts.add_argument('--raw', action='store_true', help='use raw html')
    ps_bts.add_argument('action', type=str, default=debian.bts_actions)
    ps_bts.set_defaults(func=lambda ag: debian.bts(ag.id, ag.action, raw=ag.raw))

    # == cmd ==
    ag.add_argument('--cmd', type=str, default=[], action='append',
                    help='add the command line output to the prompt')

    # -- buildd
    ps_buildd = subps.add_parser('buildd', help='buildd')
    ps_buildd.add_argument('--package', '-p', type=str, required=True)
    ps_buildd.add_argument('--suite', '-s', type=str, default='sid')
    ps_buildd.add_argument('--raw', action='store_true', help='use raw html')
    ps_buildd.add_argument('action', type=str, choices=debian.buildd_actions)
    ps_buildd.set_defaults(func=lambda ag: debian.buildd(ag.package, ag.action, suite=ag.suite, raw=ag.raw))

    # -- file (old)
    # e.g., license check (SPDX format), code improvement, code explain
    # TODO: support multiple files (nargs=+)
    ps_file = subps.add_parser('file', help='ask questions regarding a specific file')
    ps_file.add_argument('--file', '-f', type=str, required=True)
    ps_file.add_argument('action', type=str, choices=debian.file_actions)
    ps_file.set_defaults(func=lambda ag: debian.file(ag.file, ag.action))

    # -- file --
    ag.add_argument('--file', '-f', type=str, default=[], action='append',
                    help='load specified file(s) in prompt')

    # -- vote
    ps_vote = subps.add_parser('vote', help='vote.debian.org')
    ps_vote.add_argument('--suffix', '-s', type=str, required=True,
                    help='for example, 2023/vote_002')
    ps_vote.add_argument('action', type=str, choices=debian.vote_actions)
    ps_vote.set_defaults(func=lambda ag: debian.vote(ag.suffix, ag.action))

    # -- policy
    ps_policy = subps.add_parser('policy', help='policy document (plain text)')
    ps_policy.add_argument('--section', '-s', type=str, required=True)
    ps_policy.add_argument('action', type=str, choices=debian.policy_actions)
    ps_policy.set_defaults(func=lambda ag: debian.policy(ag.section, ag.action))

    # -- devref
    ps_devref = subps.add_parser('devref', help='devref document')
    ps_devref.add_argument('--section', '-s', type=str, required=True)
    ps_devref.add_argument('action', type=str, choices=debian.devref_actions)
    ps_devref.set_defaults(func=lambda ag: debian.devref(ag.section, ag.action))

    # -- man page
    ps_man = subps.add_parser('man', help='manual page')
    ps_man.add_argument('--man', '-m', type=str, required=True)
    ps_man.add_argument('action', type=str, choices=debian.man_actions)
    ps_man.set_defaults(func=lambda ag: debian.man(ag.man, ag.action))

    # -- tldr page
    ag.add_argument('--tldr', type=str, default=[], action='append',
                    help='add tldr page to the prompt.')

    # -- dev mode
    ps_dev = subps.add_parser('dev', aliases=['x'], help='code editing with context')
    ps_dev.add_argument('--file', '-f', type=str, required=True,
                        help='path to file you want to edit')
    ps_dev.add_argument('--policy', type=str, default=None,
                        help='which section of policy to look at?')
    ps_dev.add_argument('action', type=str, choices=debian.dev_actions)
    ps_dev.set_defaults(func=lambda ag: debian.dev(ag.file, ag.action,
                        policy=ag.policy, debgpt_home=ag.debgpt_home))

    # question templates
    ag.add_argument('--ask', '-A', type=str, default=debian.QUESTIONS[':none'])

    # -- parse and sanitize
    ag = ag.parse_args()
    return ag


def interactive_mode(f: frontend.AbstractFrontend, ag):
        # create prompt_toolkit style
        prompt_style = Style(
            [('prompt', 'bold fg:ansibrightcyan'), ('', 'bold ansiwhite')])
        prompt_session = PromptSession(style=prompt_style, multiline=ag.multiline)
        try:
            while text := prompt_session.prompt(f'{os.getlogin()}[{len(f.session)}]> '):
                if f.stream:
                    console.print(
                        f'[bold green]LLM[{1+len(f.session)}]>[/bold green] ', end='')
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

def main():
    # parse args and prepare debgpt_home
    ag = parse_args()
    if ag.verbose:
        console.log(ag)

    # initialize the frontend
    f = frontend.create_frontend(ag)

    # create task-specific prompts. note, some special tasks will exit()
    # in their subparser default function when then finished, such as backend
    msg = ag.func(ag)
    # XXX: on migration to new cli design
    # FIXME: add these contents following the commandline argument order.
    if ag.file:
        msg = '' if msg is None else msg
        for file_path in ag.file:
            info = debian.file(file_path, 'blank')
            msg += '\n' + info
    if ag.tldr:
        msg = '' if msg is None else msg
        for tldr_name in ag.tldr:
            info = debian.tldr(tldr_name)
            msg += '\n' + info
    if ag.cmd:
        msg = '' if msg is None else msg
        for cmd_line in ag.cmd:
            info = debian.command_line(cmd_line)
            msg += '\n' + info
    # --ask should be processed as the last one
    if ag.ask:
        # append customized question template to the prompt
        if ag.ask.startswith(':'):
            # is a question template from debian.QUESTIONS
            question = debian.QUESTIONS[ag.ask]
            msg += '\n' + question
        else:
            # is a user-specified question in the command line
            question = ag.ask
            msg += '\n' + question

    # in dryrun mode, we simply print the generated initial prompts
    # then the user can copy the prompt, and paste them into web-based
    # LLMs like the free web-based ChatGPT (OpenAI), claude.ai (Anthropic),
    # Bard (google), Gemini (google), huggingchat (huggingface), etc.
    if ag.frontend == 'dryrun':
        console.print(msg)
        exit()

    # print the prompt and do the first query, if specified
    if msg is not None:
        if not ag.hide_first_prompt:
            console.print(Panel(escape(msg), title='Initial Prompt'))

        # query the backend
        if f.stream:
            console.print(
                f'[bold green]LLM [{1+len(f.session)}]>[/bold green] ', end='')
            reply = f(msg)
        else:
            with Status('LLM', spinner='line'):
                reply = f(msg)
            console.print(Panel(escape(reply), title='LLM Reply'))
        # console.print('LLM>', reply)

    # drop the user into interactive mode if specified (-i)
    if not ag.quit:
        interactive_mode(f, ag)

    # dump session to json
    f.dump()
    if ag.output is not None:
        if os.path.exists(ag.output):
            console.print(f'[red]! destination {ag.output} exists. Will not overwrite this file.[/red]')
        else:
            with open(ag.output, 'wt') as fp:
                fp.write(f.session[-1]['content'])

    # some notifications
    if any(x in sys.argv for x in ('vote',)):
        # sensitive category
        console.print(Panel('''[bold white on red]LLM may hallucinate and generate incorrect contents. Please further judge the correctness of the information, and do not let LLM mislead your decision on sensitive tasks, such as debian voting.[/bold white on red]''', title='!!! Warning !!!'))
    else:
        pass


if __name__ == '__main__':
    main()
