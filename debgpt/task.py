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
import rich
import os
import sys
from . import frontend
from . import debian
from . import defaults
from rich.panel import Panel
import tempfile
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


def task_git(ag) -> None:
    console.print("[red]debgpt: git: no subcommand specified. Don[/red]")
    exit(1)


def task_git_commit(ag) -> None:
    f = ag.frontend_instance
    msg = "Previous commit titles:\n"
    msg += "```"
    msg += debian.command_line('git log --pretty=format:%s --max-count=10')
    msg += "```"
    msg += "\n"
    msg += "Change diff:\n"
    msg += "```\n"
    msg += debian.command_line('git diff --staged')
    msg += "```\n"
    msg += "\n"
    msg += defaults.QUESTIONS[':git-commit']
    frontend.query_once(f, msg)
    tmpfile = tempfile.mktemp()
    commit_message = f.session[-1]['content']
    commit_message += "\n\n<Explain why change was made.>"
    with open(tmpfile, 'wt') as tmp:
        tmp.write(commit_message)
    os.system(f'git commit -F {tmpfile}')
    os.remove(tmpfile)
    note_message = """
Please replace the <Explain why change was made.> in the git commit
message body by running:

    $ git commit --amend

or

    $ git citool --amend
"""
    console.print(Panel(note_message, title='Notice', border_style='green'))

    exit(0)


def task_fortune(ag):
    '''
    fortune mode. Note, it is very recommended to set --temperature to a value
    larger than 1.0, or LLM will give you the same thing across multiple runs.
    '''
    # create prompt
    if ag.ask.startswith(':'):
        try:
            # use a template from defaults.FORTUNE_QUESTIONS
            msg = defaults.FORTUNE_QUESTIONS[ag.ask]
        except KeyError:
            console.print('Available question templates for argument -A/--ask:')
            defaults.print_fortune_question_templates()
            exit(1)
    else:
        msg = ag.ask
    # let frontend work
    f = ag.frontend_instance
    frontend.query_once(f, msg)
    # exit
    exit(0)
