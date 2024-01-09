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
import re
import os
import sys
from . import frontend
from . import debian
from . import defaults
from .task import *
import tempfile
import rich
from collections import defaultdict
console = rich.get_console()


def version() -> None:
    from debgpt import __version__, __copyright__, __license__
    console.print(
        f'DebGPT {__version__}; Copyright {__copyright__}; Released under {__license__} license.')


def parse_args(argv):
    '''
    argparse with subparsers
    '''
    # if ~/.debgpt/config.toml exists, parse it to override the built-in defaults.
    conf = defaults.Config()
    # override the loaded configurations again with command line arguments
    ag = argparse.ArgumentParser()

    # CLI Behavior / Frontend Arguments
    ag.add_argument('--quit', '-Q', action='store_true',
                    help='directly quit after receiving the first response from LLM, instead of staying in interation.')
    ag.add_argument('--multiline', '-M', action='store_true',
                    help='enable multi-line input for prompt_toolkit. use Meta+Enter to accept the input instead.')
    ag.add_argument('--hide_first', '-H', action='store_true',
                    help='hide the first (generated) prompt; do not print argparse results')
    ag.add_argument('--verbose', '-v', action='store_true',
                    help='verbose mode. helpful for debugging')
    ag.add_argument('--output', '-o', type=str, default=None,
                    help='write the last LLM message to specified file')
    ag.add_argument('--version', action='store_true',
                    help='show DebGPT software version and quit.')
    ag.add_argument('--debgpt_home', type=str, default=conf['debgpt_home'],
                    help='directory to store cache and sessions.')
    ag.add_argument('--frontend', '-F', type=str, default=conf['frontend'],
                    choices=('dryrun', 'zmq', 'openai'))

    # LLM Inference Arguments
    ag.add_argument('--temperature', '-T', type=float, default=conf['temperature'],
                    help='''Sampling temperature. Typically ranges within [0,1]. \
Low values like 0.2 gives more focused (coherent) answer. \
High values like 0.8 gives a more random (creative) answer. \
Not suggested to combine this with with --top_p. \
See https://platform.openai.com/docs/api-reference/chat/create \
    ''')
    ag.add_argument('--top_p', '-P', type=float, default=conf['top_p'])

    # Specific to OpenAI Frontend
    ag.add_argument('--openai_base_url', type=str,
                    default=conf['openai_base_url'])
    ag.add_argument('--openai_api_key', type=str,
                    default=conf['openai_api_key'])
    ag.add_argument('--openai_model', type=str, default=conf['openai_model'])

    # Specific to ZMQ Frontend
    ag.add_argument('--zmq_backend', type=str, default=conf['zmq_backend'],
                    help='the ZMQ frontend endpoint')

    # Prompt Loaders (numbered list). You can specify them multiple times.
    # for instance, `debgpt -H -f foo.py -f bar.py`.
    # -- 1. Debian BTS
    ag.add_argument('--bts', type=str, default=[], action='append',
                    help='Retrieve BTS webpage to prompt. example: "src:pytorch", "1056388"')
    ag.add_argument('--bts_raw', action='store_true',
                    help='load raw HTML instead of plain text.')
    # -- 2. Custom Command Line(s)
    ag.add_argument('--cmd', type=str, default=[], action='append',
                    help='add the command line output to the prompt')
    # -- 3. Debian Buildd
    ag.add_argument('--buildd', type=str, default=[], action='append',
                    help='Retrieve buildd page for package to prompt.')
    # -- 4. Arbitrary Plain Text File(s)
    ag.add_argument('--file', '-f', type=str, default=[], action='append',
                    help='load specified file(s) in prompt')
    # -- 5. Debian Policy
    ag.add_argument('--policy', type=str, default=[], action='append',
                    help='load specified policy section(s). (e.g., "1", "4.6")')
    # -- 6. Debian Developers References
    ag.add_argument('--devref', type=str, default=[], action='append',
                    help='load specified devref section(s).')
    # -- 7. TLDR Manual Page
    ag.add_argument('--tldr', type=str, default=[], action='append',
                    help='add tldr page to the prompt.')
    # -- 8. Man Page
    ag.add_argument('--man', type=str, default=[], action='append',
                    help='add man page to the prompt. Note the context length!')
    # -- 9. Arbitrary HTML document
    ag.add_argument('--html', type=str, default=[], action='append',
                    help='load HTML document from given URL(s)')
    # -- 999. The Question Template at the End of Prompt
    ag.add_argument('--ask', '-A', type=str, default=defaults.QUESTIONS[':none'],
                    help="Question template to append at the end of the prompt. "
                    + "Specify ':' for printing all available templates. "
                    + "Or a customized string not starting with the colon.")

    # Task Specific Subparsers
    subps = ag.add_subparsers(help='specific task handling')
    ag.set_defaults(func=lambda ag: None)  # if no subparser is specified

    # Specific to ZMQ Backend (self-hosted LLM Inference)
    ps_backend = subps.add_parser(
        'backend', help='start backend server (self-hosted LLM inference)')
    ps_backend.add_argument('--port', '-p', type=int, default=11177,
                            help='port number "11177" looks like "LLM"')
    ps_backend.add_argument('--host', type=str, default='tcp://*')
    ps_backend.add_argument('--backend_impl', type=str,
                            default='zmq', choices=('zmq',))
    ps_backend.add_argument('--max_new_tokens', type=int, default=512)
    ps_backend.add_argument('--llm', type=str, default='Mistral7B')
    ps_backend.add_argument('--device', type=str, default='cuda')
    ps_backend.add_argument('--precision', type=str, default='fp16')
    ps_backend.set_defaults(func=task_backend)

    # Task: git
    ps_git = subps.add_parser('git', help='git command wrapper')
    ps_git.set_defaults(func=task_git)
    git_subps = ps_git.add_subparsers(help='git commands')
    # Task: git commit
    ps_git_commit = git_subps.add_parser('commit', aliases=['co'],
                                         help='directly commit staged changes with auto-generated message')
    ps_git_commit.set_defaults(func=task_git_commit)

    # Task: replay
    ps_replay = subps.add_parser(
        'replay', help='replay a conversation from a JSON file')
    ps_replay.add_argument('json_file_path', type=str,
                           help='path to the JSON file')
    ps_replay.set_defaults(func=task_replay)

    # Task: stdin
    ps_stdin = subps.add_parser(
        'stdin', help='read stdin as the first prompt. Should combine with -Q.')
    ps_stdin.set_defaults(func=lambda ag: debian.stdin())

    # Task: fortune
    ps_fortune = subps.add_parser('fortune', help='fortune mode. Note, it is \
very recommended to set --temperature to a value larger than 1.0, or LLM will \
give you the same thing across multiple runs.')
    ps_fortune.add_argument('ask', type=str, nargs='?', default=':fun',
                            help='specify what type of fortune you want')
    ps_fortune.set_defaults(func=task_fortune)

    # -- parse and sanitize
    ag = ag.parse_args(argv)
    return ag


def parse_args_order(argv) -> List[str]:
    '''
    parse the order of selected arguments

    We want `debgpt -f file1.txt -f file2.txt` generate different results
    than    `debgpt -f file2.txt -f file1.txt`. But the standard argparse
    will not reserve the order.

    For example, we need to match
    -f, --file, -Hf (-[^-]*f), into --file
    '''
    order : List[str] = []
    def _match_ls(probe: str, long: str, short: str, dest: List[str]):
        if any(probe == x for x in (long, short)) \
                or any(probe.startswith(x+'=') for x in (long, short)) \
                or re.match(r'-[^-]*'+short[-1], probe):
            dest.append(long.lstrip('--'))
    def _match_l(probe: str, long: str, dest: List[str]):
        if probe == long or probe.startswith(long+'='):
            dest.append(long.lstrip('--'))
    for item in argv:
        _match_l(item, '--bts', order)
        _match_l(item, '--cmd', order)
        _match_l(item, '--buildd', order)
        _match_ls(item, '--file', '-f', order)
        _match_l(item, '--policy', order)
        _match_l(item, '--devref', order)
        _match_l(item, '--tldr', order)
        _match_l(item, '--man', order)
        _match_l(item, '--html', order)
    return order


def gather_information_ordered(msg: Optional[str], ag, ag_order) -> Optional[str]:
    '''
    based on the argparse results, as well as the argument order, collect
    the specified information into the first prompt. If none specified,
    return None.
    '''
    def _append_info(msg: str, info: str) -> str:
        msg = '' if msg is None else msg
        return msg + '\n' + info

    # following the argument order, dispatch to debian.* functions with
    # different function signatures
    for key in ag_order:
        if key in ('file', 'tldr', 'man', 'buildd'):
            spec = getattr(ag, key).pop(0)
            func = getattr(debian, key)
            msg = _append_info(msg, func(spec))
        elif key == 'cmd':
            cmd_line = ag.cmd.pop(0)
            msg = _append_info(msg, debian.command_line(cmd_line))
        elif key == 'bts':
            bts_id = ag.bts.pop(0)
            msg = _append_info(msg, debian.bts(bts_id, raw=ag.bts_raw))
        elif key == 'html':
            url = ag.html.pop(0)
            msg = _append_info(msg, debian.html(url, raw=False))
        elif key in ('policy', 'devref'):
            spec = getattr(ag, key).pop(0)
            func = getattr(debian, key)
            msg = _append_info(msg, func(spec, debgpt_home=ag.debgpt_home))
        else:
            raise NotImplementedError(key)

    # --ask should be processed as the last one
    if ag.ask:
        msg = '' if msg is None else msg
        # append customized question template to the prompt
        if ag.ask in ('?', ':', ':?'):
            # ":?" means to print available options and quit
            console.print(
                'Available question templates for argument -A/--ask:')
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

    return msg


def interactive_mode(f: frontend.AbstractFrontend, ag):
    # create prompt_toolkit style
    prompt_style = Style([('prompt', 'bold fg:ansibrightcyan'),
                          ('', 'bold ansiwhite')])
    prompt_session = PromptSession(style=prompt_style, multiline=ag.multiline)
    try:
        while text := prompt_session.prompt(f'{os.getlogin()}[{len(f.session)}]> '):
            frontend.query_once(f, text)
    except EOFError:
        pass
    except KeyboardInterrupt:
        pass


def main(argv=sys.argv[1:]):
    # parse args and prepare debgpt_home
    ag = parse_args(argv)
    if ag.version:
        version()
        exit(0)
    if ag.verbose:
        console.log(ag)

    # parse argument order
    ag_order = parse_args_order(argv)
    if ag.verbose:
        console.log('Argument Order:', ag_order)

    # initialize the frontend
    f = frontend.create_frontend(ag)
    ag.frontend_instance = f

    # create task-specific prompts. note, some special tasks will exit()
    # in their subparser default function when then finished, such as backend,
    # version, etc. They will exit.
    msg = ag.func(ag)

    # gather all specified information in the initial prompt,
    # such as --file, --man, --policy, --ask
    msg = gather_information_ordered(msg, ag, ag_order)

    # in dryrun mode, we simply print the generated initial prompts
    # then the user can copy the prompt, and paste them into web-based
    # LLMs like the free web-based ChatGPT (OpenAI), claude.ai (Anthropic),
    # Bard (google), Gemini (google), huggingchat (huggingface), etc.
    if ag.frontend == 'dryrun':
        console.print(msg)
        exit(0)

    # print the prompt and do the first query, if specified
    if msg is not None:
        if not ag.hide_first:
            console.print(Panel(escape(msg), title='Initial Prompt'))

        # query the backend
        frontend.query_once(f, msg)

    # drop the user into interactive mode if specified (-i)
    if not ag.quit:
        interactive_mode(f, ag)

    # dump session to json
    f.dump()
    if ag.output is not None:
        if os.path.exists(ag.output):
            console.print(
                f'[red]! destination {ag.output} exists. Will not overwrite this file.[/red]')
        else:
            with open(ag.output, 'wt') as fp:
                fp.write(f.session[-1]['content'])


if __name__ == '__main__':
    main()
