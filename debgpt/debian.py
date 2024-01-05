# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
'''
This file is in charge of organizaing (debian specific) user prompts,
which are subsequently sent through frontend to the backend for LLM to process.
'''
from typing import *
import re
import requests
import pytest
from . import policy as debgpt_policy
import os
import subprocess
import sys


########################
# Question templates
########################

QUESTIONS = {
    ':none': '',
    ':free': 'Read the above information carefully, and I will ask you questions later. Be quiet for now.',
    }

########################
# Utility I/O functions
########################


def _load_html(url: str) -> List[str]:
    '''
    read HTML from url, convert it into plain text, then list of lines
    '''
    from bs4 import BeautifulSoup
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    text = soup.get_text().strip()
    text = re.sub('\n\n+\n', '\n\n', text)
    text = [x.strip() for x in text.split('\n')]
    return text


def _load_html_raw(url: str) -> List[str]:
    '''
    read the raw HTML.
    XXX: if we do not preprocess the raw HTML, the input sequence to LLM
    will be very long. It may trigger CUDA out-of-memory in the backend
    when the length exceeds a certain value, depending on the CUDA memory
    available in the backend machine.
    '''
    r = requests.get(url)
    text = r.text.strip()
    text = re.sub('\n\n+\n', '\n\n', text)
    text = [x.strip() for x in text.split('\n')]
    return text


def _load_file(path: str) -> List[str]:
    with open(path, 'rt') as f:
        lines = [x.rstrip() for x in f.readlines()]
    return lines


def _load_cmdline(cmd: Union[str, List]) -> List[str]:
    if isinstance(cmd, str):
        cmd = cmd.split(' ')
    stdout = subprocess.check_output(cmd).decode()
    lines = [x.rstrip() for x in stdout.split('\n')]
    return lines


def _load_stdin() -> List[str]:
    lines = [x.rstrip() for x in sys.stdin.readlines()]
    return lines


# == mailing list ==
mailing_list_actions = ('summary', 'reply', 'free')


def mailing_list(url: str, action: str, *, raw: bool = False):
    text = _load_html_raw(url) if raw else _load_html(url)
    lines = ['The following is an email from a mailing list thread:']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'summary':
        lines.append('Could you please summarize this email for me?')
    elif action == 'reply':
        lines.append('Could you please try to reply this email?')
    elif action == 'free':
        lines.append(
            'Read this email carefully. Next I will ask you a few questions about it.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', mailing_list_actions)
def test_mailing_list(action):
    url = 'https://lists.debian.org/debian-project/2023/12/msg00029.html'
    print(mailing_list(url, action))


# == buildd ==
buildd_actions = ('status', 'free')


def buildd(p: str, action: str, *, suite: str = 'sid', raw: bool = False):
    url = f'https://buildd.debian.org/status/package.php?p={p}&suite={suite}'
    text = _load_html_raw(url) if raw else _load_html(url)
    lines = [
        f'The following is the webpage about the build status of package {p}:']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'status':
        lines.append('Briefly describe the build status of this package. Organize the information in a pretty table if possible (you can use unicode tabular characters). If it failed on some architectures, briefly list them and explain the reasons.')
    elif action == 'free':
        lines.append(
            'Read this webpage carefully. I will ask you a few questions next.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', buildd_actions)
def test_buildd(action):
    print(buildd('pytorch', action))


# == bts ==
bts_actions = ('summary', 'free')


def bts(identifier: str, action: str, *, raw: bool = False):
    url = f'https://bugs.debian.org/{identifier}'
    text = _load_html_raw(url) if raw else _load_html(url)
    lines = ["The following is a webpage from Debian's bug tracking system:"]
    lines.extend(['```'] + text + ['```', ''])
    if action == 'summary':
        lines.append(
            'Could you please summarize the webpage? If possible, you can organize the information in a pretty table with ANSI tabular characters.')
    elif action == 'free':
        lines.append(
            'Read this webpage carefully. Next I will ask you a few questions about it.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', bts_actions)
def test_bts(action):
    print(bts('src:pytorch', action))
    print(bts('1056388', action))


# == vote ==
vote_actions = ('summary', 'diff', 'free')


def vote(suffix: str, action: str):
    url = f'https://www.debian.org/vote/{suffix}'
    text = _load_html(url)
    lines = ['The following is a webpage about a General Resolution.']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'summary':
        lines.append(
            'Please summarize these proposals. You can use tabular format if it can better represent the information.')
    elif action == 'diff':
        lines.append(
            'Please explain the differences among those proposals. You can use tabular format if it can better represent the information.')
    elif action == 'free':
        lines.append(
            'Read this webpage carefully, and I will ask you questions later. Be quiet for now.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', vote_actions)
def test_vote(action):
    print(vote('2023/vote_002', action))


# == policy ==
policy_actions = ('polish', 'free')


def policy(section: str, action: str, *,
           debgpt_home: str = os.path.expanduser('~/.debgpt')):
    if not os.path.exists(debgpt_home):
        os.mkdir(debgpt_home)
    doc = debgpt_policy.DebianPolicy(os.path.join(debgpt_home, 'policy.txt'))
    text = doc[section].split('\n')
    lines = [f'''The following is the section {section} of Debian Policy:''']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'polish':
        lines.append('Please polish the language enclosed by the "```" marks. While polishing this document, the language must be precise. Additionally, any vague or ambiguous language is not acceptable. Furthermore, do not change the original meaning of the text while polishing. Now go ahead.')
    elif action == 'free':
        lines.append(
            'Please carefully read this document. I will ask questions later. Be quiet now.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', policy_actions)
def test_policy(action):
    print(policy('4.6', action))


# == devref ==
devref_actions = ('free',)


def devref(section: str, action: str, *,
           debgpt_home: str = os.path.expanduser('~/.debgpt')):
    if not os.path.exists(debgpt_home):
        os.mkdir(debgpt_home)
    doc = debgpt_policy.DebianDevref(os.path.join(debgpt_home, 'devref.txt'))
    text = doc[section].split('\n')
    lines = [
        f'''The following is the section {section} of Debian Developer's Reference:''']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'free':
        lines.append(
            'Please carefully read this document. I will ask questions later. For now please be quiet.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', devref_actions)
def test_devref(action):
    print(devref('5.5', action))


# == man and tldr ==
man_actions = ('free',)


def man(name: str, action: str):
    text = _load_cmdline(f'man {name}')
    lines = [
        f'''The following is the contents of the manual page for {name}, as enclosed by "```" marks.''']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'free':
        lines.append(
            'Read it carefully. I will ask you questions later. For now please be quiet.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


def tldr(name: str):
    text = _load_cmdline(f'tldr {name}')
    lines = [f'''The following is the tldr of the program {name}:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


# == stdin ==
# empty tuple. We don't know what the user wants. stdin is too flexible.
stdin_actions = ()


def stdin():
    text = _load_stdin()
    return '\n'.join(text)


def test_stdin():
    # I dont know how to test this but the two lines of code does not seem to have bug.
    pass


# == file ==
file_actions = ('what', 'brief', 'licensecheck', 'free', 'none', 'blank')


def file(path: str, action: str):
    text = _load_file(path)
    if action == 'none':
        return '\n'.join(text)
    lines = [f'''The following is a file named {path}:''']
    lines.extend(['```'] + text + ['```', ''])
    if action == 'what':
        lines.append(
            '''What is the purpose of this file? Please explain in detail.''')
    elif action == 'brief':
        lines.append(
            '''Briefly explain the purpose of this file. Your answer must not exceed the twitter number of character limit.''')
    elif action == 'licensecheck':
        lines.append(
            'What is the copyright and license of this file? Use SPDX format.')
    elif action == 'free':
        lines.append(
            'Read this file carefully. Next I will ask you a few questions about it.')
    elif action == 'blank':
        # XXX: for new cli design
        pass
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


@pytest.mark.parametrize('action', file_actions)
def test_file(action):
    print(file('debgpt/__init__.py', action))


# === dev (abbr: x) ===
dev_actions = ('free',)


def dev(path: str, action: str, *,
        policy: str = None,
        debgpt_home: str = os.path.expanduser('~/.debgpt'),
        ):
    '''
    the file-to-edit is path
    the additional information, such as policy, are used to LLM to learn
    how to make specified changes.
    '''
    # load the file to develop
    text_of_interest = _load_file(path)
    lines = [
        f'''The following is the content of a file named `{path}`, enclosed by the "```" mark:''']
    lines.extend(['```'] + text_of_interest + ['```', ''])
    lines.append('Read this file carefully.')

    # load policy section if specified
    if policy is not None:
        if not os.path.exists(debgpt_home):
            os.mkdir(debgpt_home)
        doc = debgpt_policy.DebianPolicy(
            os.path.join(debgpt_home, 'policy.txt'))
        text = doc[policy].split('\n')
        lines.append('')
        lines.append(
            f'''The following is the section {policy} of Debian Policy, enclosed by the "```" marks:''')
        lines.extend(['```'] + text + ['```', ''])

    if action == 'free':
        lines.append(
            f'Later I will ask you to edit the provided file `{path}` and generate a unix-format patch. The other information, if provided, might help you make the specified edits later. Please be quiet for now and wait for the instruction.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)
