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
from typing import List, Union
import re
import requests
from . import policy as debgpt_policy
from bs4 import BeautifulSoup
import os
import subprocess
import sys
import rich
console = rich.get_console()

__doc__ = '''
This file is in charge of organizaing (debian specific) functions for loading
texts from various sources, which are subsequently combined into the first
prompt, and sent through frontend to the backend for LLM to process.
'''

########################
# Utility I/O functions
########################


def _load_html(url: str) -> List[str]:
    '''
    read HTML from url, convert it into plain text, then list of lines
    '''
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    text = soup.get_text().strip()
    text = re.sub('\n\n+\n', '\n\n', text)
    text = [x.rstrip() for x in text.split('\n')]
    return text


def _load_bts(identifier: str) -> List[str]:
    url = f'https://bugs.debian.org/{identifier}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")

    if not identifier.startswith('src:'):
        # delete useless system messages
        _ = [x.clear() for x in soup.find_all('p', attrs={'class': 'msgreceived'})]
        _ = [x.clear() for x in soup.find_all('div', attrs={'class': 'infmessage'})]

    text = soup.get_text().strip()
    text = re.sub('\n\n+\n', '\n\n', text)
    text = [x.strip() for x in text.split('\n')]

    # filter out useless information from the webpage
    if identifier.startswith('src:'):
        # the lines from 'Options' to the end are useless
        text = text[: text.index('Options')]

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


#####################################
# Text Loaders from Various Sources
#####################################


def archw(identifier: str):
    '''
    Archwiki. e.g.,
    https://wiki.archlinux.org/title/Archiving_and_compression
    '''
    url = f'https://wiki.archlinux.org/title/{identifier}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features='html.parser')
    text = soup.get_text().split('\n')
    lines = [f'Here is the Arch Wiki about {identifier}:']
    lines.extend(['```', *text, '```', ''])
    return '\n'.join(lines)


def html(url: str, *, raw: bool = False):
    '''
    Load a website in plain/raw text format
    '''
    text = _load_html_raw(url) if raw else _load_html(url)
    lines = [f'Here is the contents of {url}:']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def buildd(p: str, *, suite: str = 'sid', raw: bool = False):
    url = f'https://buildd.debian.org/status/package.php?p={p}&suite={suite}'
    text = _load_html_raw(url) if raw else _load_html(url)
    lines = [
        f'The following is the build status of package {p}:']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def bts(identifier: str, *, raw: bool = False):
    text = _load_bts(identifier)
    lines = ["The following is a webpage from Debian's bug tracking system:"]
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


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


def file(path: str):
    if ':' in path:
        # it is a special syntax to specify line range e.g. setup.py:1-10
        path, lrange = path.split(':')
        text = _load_file(path)
        start, end = re.match(r'^(\d*)-(\d*)', lrange).groups()
        start = int(start) if start else None
        end = int(end) if end else None
        text = text[start:end]
    else:
        text = _load_file(path)
    lines = [f'''The following is a file named {path}:''']
    lines.extend(['```'] + text + ['```', ''])
    return '\n'.join(lines)


def pynew(version_section: str):
    '''
    What's New websites of cpython
    https://docs.python.org/3/whatsnew/3.12.html#summary-release-highlights

    version: e.g. 3.12
    section: e.g. summary
    '''
    # parse inputs
    if ':' in version_section:
        # normally return the specified section
        version, section = version_section.split(':')
    else:
        # print all available sections and exit()
        version, section = version_section, None
    # retrieve webpage
    url = f'https://docs.python.org/3/whatsnew/{version}.html'
    doc = requests.get(url).text
    soup = BeautifulSoup(doc, features='html.parser')
    sections = [x.attrs['id'] for x in soup.find_all('section')]
    # extract information from webpage
    if section is None or not section:
        # if not specified section: print available ones and exit()
        console.print("Available Sections in Python What's New:", sections)
        sys.exit(0)
    else:
        # if specified section: find that section
        part = soup.find_all('section', attrs={'id': section})[0]
        text = part.get_text().strip()
    # enclose in markdown block
    lines = [f'''The following is the {section} section of Python {version}'s What's New document:''']
    lines.extend(['```', text, '```', ''])
    return '\n'.join(lines)
