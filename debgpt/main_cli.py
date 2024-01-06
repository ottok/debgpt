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
import tempfile
import rich
console = rich.get_console()


def version() -> None:
    from debgpt import __version__, __copyright__, __license__
    console.print(f'DebGPT {__version__}; Copyright {__copyright__}; Released under {__license__} license.')


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


def task_git(ag) -> None:
    console.print("[red]debgpt: git: no subcommand specified. Don[/red]")
    exit(1)


def task_git_commit(ag) -> None:
    f = ag.frontend_instance
    msg = debian.command_line('git diff --staged')
    msg += '\n' + defaults.QUESTIONS[':git-commit']
    if f.stream:
        console.print(
            f'[bold green]LLM [{1+len(f.session)}]>[/bold green] ', end='')
        reply = f(msg)
    else:
        with Status('LLM', spinner='line'):
            reply = f(msg)
        console.print(Panel(escape(reply), title='LLM Reply'))
    tmpfile = tempfile.mktemp()
    commit_message = f.session[-1]['content']
    debgpt_cmd = ' '.join([os.path.basename(sys.argv[0]), *sys.argv[1:]])
    commit_message += f'''\n\nNote, this commit message is automatically generated by `{debgpt_cmd}`'''
    with open(tmpfile, 'wt') as tmp:
        tmp.write(commit_message)
    os.system(f'git commit -F {tmpfile}')
    os.remove(tmpfile)
    note_message = '''\
If you are not satisfied with the above git commit message you may use the following command to retry:

    $ git reset --soft HEAD~1 ; debgpt git commit

Or if you want to manually edit the commit message with:

    $ git commit --amend\
'''
    console.print(Panel(note_message, title='Notice', border_style='green'))

    exit(0)


def parse_args():
    '''
    argparse with subparsers
    '''
    conf = defaults.Config()
    ag = argparse.ArgumentParser()

    # LLM inference arguments
    ag.add_argument('--temperature', '-T', type=float, default=conf['temperature'],
        help='''Sampling temperature. Typically ranges within [0,1]. \
Low values like 0.2 gives more focused (coherent) answer. \
High values like 0.8 gives a more random (creative) answer. \
Not suggested to combine this with with --top_p. \
See https://platform.openai.com/docs/api-reference/chat/create \
    ''')
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
    ag.add_argument('--version', action='store_true', help='show DebGPT software version and quit.')

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

    # -- git (special mode)
    ps_git = subps.add_parser('git', help='special mode: git helper')
    ps_git.set_defaults(func=task_git)
    git_subps = ps_git.add_subparsers(help='git commands')
    #    -- git commit
    ps_git_commit = git_subps.add_parser('commit', help='commit staged changes with auto-generated message')
    ps_git_commit.set_defaults(func=task_git_commit)

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
    ag.add_argument('--bts', type=str, default=[], action='append',
                    help='Retrieve BTS webpage. example: "src:pytorch", "1056388"')
    ag.add_argument('--bts_raw', action='store_true', help='load raw HTML instead of plain text.')


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
    ag.add_argument('--policy', type=str, default=[], action='append',
                    help='load specified policy section(s). (e.g., "1", "4.6")')

    # -- devref
    ag.add_argument('--devref', type=str, default=[], action='append',
                    help='load specified devref section(s).')

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
    ag.add_argument('--ask', '-A', type=str, default=defaults.QUESTIONS[':none'])

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
    if ag.version:
        version()
        exit()
    if ag.verbose:
        console.log(ag)

    # initialize the frontend
    f = frontend.create_frontend(ag)
    ag.frontend_instance = f

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
    if ag.bts:
        msg = '' if msg is None else msg
        for bts_id in ag.bts:
            info = debian.bts(bts_id, raw=ag.bts_raw)
            msg += '\n' + info
    if ag.policy:
        msg = '' if msg is None else msg
        for section in ag.policy:
            info = debian.policy(section, debgpt_home=ag.debgpt_home)
            msg += '\n' + info
    if ag.devref:
        msg = '' if msg is None else msg
        for section in ag.devref:
            info = debian.devref(section, debgpt_home=ag.debgpt_home)
            msg += '\n' + info
    # --ask should be processed as the last one
    if ag.ask:
        msg = '' if msg is None else msg
        # append customized question template to the prompt
        if ag.ask in ('?', ':', ':?'):
            # ":?" means to print available options and quit
            console.print('Available question templates for argument -A/--ask:')
            defaults.print_question_templates()
            exit(0)
        if ag.ask.startswith(':'):
            # specifies a question template from defaults.QUESTIONS
            question = defaults.QUESTIONS[ag.ask]
            msg += '\n' + question
        else:
            # is a user-specified question in the command line
            question = ag.ask
            msg += ('' if not msg else '\n') + question

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
