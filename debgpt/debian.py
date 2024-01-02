# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
'''
This file is in charge of organizaing (debian specific) user prompts,
which are subsequently sent through frontend to the backend for LLM to process.
'''
from typing import *
import pytest
from bs4 import BeautifulSoup
import requests

def mailing_list(url: str, action: str):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    text = soup.get_text().strip()
    text = [x.strip() for x in text.split('\n')]
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
        raise NotImplementedError('reply')
    return '\n'.join(lines)



def test_mailing_list_page():
    url = 'https://lists.debian.org/debian-project/2023/12/msg00029.html'
    content = mailing_list(url, 'summary')
    print(content)
    content = mailing_list(url, 'reply')
    print(content)
