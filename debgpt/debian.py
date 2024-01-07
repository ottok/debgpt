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
from .defaults import QUESTIONS


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


def buildd(p: str, *, suite: str = 'sid', raw: bool = False):
    url = f'https://buildd.debian.org/status/package.php?p={p}&suite={suite}'
    text = _load_html_raw(url) if raw else _load_html(url)
    lines = [
        f'The following is the build status of package {p}:']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def bts(identifier: str, *, raw: bool = False):
    url = f'https://bugs.debian.org/{identifier}'
    text = _load_html_raw(url) if raw else _load_html(url)

    # filter out useless information from the webpage
    if identifier.startswith('src:') and not raw:
        # the lines from 'Options' to the end are useless
        text = text[: text.index('Options')]

    lines = ["The following is a webpage from Debian's bug tracking system:"]
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


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


def policy(section: str, *, debgpt_home: str):
    '''
    the policy cache in plain text format will be stored in debgpt_home
    '''
    doc = debgpt_policy.DebianPolicy(os.path.join(debgpt_home, 'policy.txt'))
    text = doc[section].split('\n')
    lines = [f'''The following is the section {section} of Debian Policy:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def devref(section: str, *, debgpt_home: str):
    '''
    similar to policy, the devref cache will be stored in debgpt_home
    '''
    doc = debgpt_policy.DebianDevref(os.path.join(debgpt_home, 'devref.txt'))
    text = doc[section].split('\n')
    lines = [
        f'''The following is the section {section} of Debian Developer's Reference:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def man(name: str):
    text = _load_cmdline(f'man {name}')
    lines = [f'''The following is the manual page of {name}:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def tldr(name: str):
    text = _load_cmdline(f'tldr {name}')
    lines = [f'''The following is the tldr of the program {name}:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def command_line(cmd: str):
    text = _load_cmdline(cmd)
    lines = [f'''The following is the output of command line `{cmd}`:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def stdin():
    text = _load_stdin()
    return '\n'.join(text)
