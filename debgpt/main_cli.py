# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.

# suppress all warnings.
import warnings
warnings.filterwarnings("ignore")

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
    exit(1)


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
    ag.add_argument('--stream', '-S', type=bool, default=conf['stream'],
                    help='default to streaming mode when openai frontend is used')  # FIXME: this argument does not work
    ag.add_argument('--openai_model_id', type=str, default=conf['openai_model_id'])

    # CLI behavior
    ag.add_argument('--quit', '-Q', action='store_true', help='directly quit after receiving the first response from LLM, instead of staying in interation.')
    ag.add_argument('--multiline', action='store_true', help='enable multi-line input for prompt_toolkit. use Meta+Enter to accept the input instead.')
    ag.add_argument('--hide_first_prompt', '-H', action='store_true', help='hide the first (generated) prompt')

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

    # -- buildd
    ps_buildd = subps.add_parser('buildd', help='buildd')
    ps_buildd.add_argument('--package', '-p', type=str, required=True)
    ps_buildd.add_argument('--suite', '-s', type=str, default='sid')
    ps_buildd.add_argument('--raw', action='store_true', help='use raw html')
    ps_buildd.add_argument('action', type=str, choices=debian.buildd_actions)
    ps_buildd.set_defaults(func=lambda ag: debian.buildd(ag.package, ag.action, suite=ag.suite, raw=ag.raw))

    # -- file
    # e.g., license check (SPDX format), code improvement, code explain
    # TODO: support multiple files (nargs=+)
    ps_file = subps.add_parser('file', help='ask questions regarding a specific file')
    ps_file.add_argument('--file', '-f', type=str, required=True)
    ps_file.add_argument('action', type=str, choices=debian.file_actions)
    ps_file.set_defaults(func=lambda ag: debian.file(ag.file, ag.action))

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

    # -- dev mode
    ps_dev = subps.add_parser('dev', aliases=['x'], help='code editing with context')
    ps_dev.add_argument('--file', '-f', type=str, required=True,
                        help='path to file you want to edit')
    ps_dev.add_argument('--policy', type=str, default=None,
                        help='which section of policy to look at?')
    ps_dev.add_argument('action', type=str, choices=debian.dev_actions)
    ps_dev.set_defaults(func=lambda ag: debian.dev(ag.file, ag.action,
                        policy=ag.policy, debgpt_home=ag.debgpt_home))

    # -- parse and sanitize
    ag = ag.parse_args()
    if ag.frontend == 'zmq' and ag.stream == True:
        console.log('disabling streaming because it is not yet supported for ZMQ frontend')
        ag.stream = False
    return ag


def main():
    # parse args and prepare debgpt_home
    ag = parse_args()
    console.log(ag)
    if not os.path.exists(ag.debgpt_home):
        os.mkdir(ag.debgpt_home)

    # create task-specific prompts. note, some special tasks will exit()
    # in their subparser default function when then finished, such as backend
    msg = ag.func(ag)
    f = frontend.create_frontend(ag)

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
    if not ag.quit:
        # create prompt_toolkit style
        prompt_style = Style(
            [('prompt', 'bold fg:ansibrightcyan'), ('', 'bold ansiwhite')])
        prompt_session = PromptSession(style=prompt_style, multiline=ag.multiline)
        try:
            while text := prompt_session.prompt(f'{os.getlogin()} [{len(f.session)}]> '):
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
    if any(x in sys.argv for x in ('vote',)):
        # sensitive category
        console.print(Panel('''[bold white on red]LLM may hallucinate and generate incorrect contents. Please further judge the correctness of the information, and do not let LLM mislead your decision on sensitive tasks, such as debian voting.[/bold white on red]''', title='!!! Warning !!!'))
    else:
        pass


if __name__ == '__main__':
    main()
