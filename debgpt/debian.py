# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
'''
This file is in charge of organizaing (debian specific) user prompts,
which are subsequently sent through frontend to the backend for LLM to process.
'''
from typing import *
import re
import pytest
from bs4 import BeautifulSoup
import requests


def _load_html(url: str) -> List[str]:
    '''
    read HTML from url, convert it into list of lines
    '''
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    text = soup.get_text().strip()
    text = re.sub('\n\n+\n', '\n\n', text)
    text = [x.strip() for x in text.split('\n')]
    return text


def mailing_list(url: str, action: str):
    text = _load_html(url)
    lines = []
    lines.append('The following is an email from a mailing list thread:')
    lines.append('```')
    lines.extend(text)
    lines.append('```')
    if action == 'summary':
        lines.append('Could you please summarize this email for me?')
    elif action == 'reply':
        lines.append('Could you please try to reply this email?')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


def test_mailing_list_page():
    url = 'https://lists.debian.org/debian-project/2023/12/msg00029.html'
    content = mailing_list(url, 'summary')
    print(content)
    content = mailing_list(url, 'reply')
    print(content)


def bts(identifier: str, action: str):
    text = _load_html(f'https://bugs.debian.org/{identifier}')
    lines = []
    lines.append(
        '''The following is a webpage from Debian's bug tracking system:''')
    lines.append('```')
    lines.extend(text)
    lines.append('```')
    if action == 'summary':
        lines.append(
            'Could you please summarize the webpage? If possible, you can organize the information in a pretty table with ANSI tabular characters.')
    else:
        raise NotImplementedError(action)
    return '\n'.join(lines)


def test_bts():
    print(bts('src:pytorch', 'summary'))
    print(bts('1056388', 'summary'))
