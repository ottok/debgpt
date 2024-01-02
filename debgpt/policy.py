# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import sys
import os
import re
import pytest
import requests
import rich
console = rich.get_console()


class DebianPolicy(object):
    '''
    cache the plain text policy document.
    and query its sections / subsections.
    see pytest for usage example.
    '''
    URL = 'https://www.debian.org/doc/debian-policy/policy.txt'
    SEP_SECTION = '***'
    SEP_SUBSECTION = '==='
    SEP_SUBSUBSECTION = '---'

    def __init__(self, cache: str = 'policy.txt'):
        if not os.path.exists('policy.txt'):
            r = requests.get(self.URL)
            with open(cache, 'wb') as f:
                f.write(r.content)
            console.log(f'DebianPolicy> cached policy text at {cache}')
        with open(cache, 'rt') as f:
            self.lines = [x.rstrip() for x in f.readlines()]
    def __getitem__(self, index: str):
        sep = {1: self.SEP_SECTION, 2: self.SEP_SUBSECTION,
               3: self.SEP_SUBSUBSECTION}[len(index.split('.'))]
        ret = []
        prev = ''
        in_range = False
        for cursor in self.lines:
            if cursor.startswith(sep) and prev.startswith(f'{index}. '):
                # start
                ret.append(prev)
                ret.append(cursor)
                in_range = True
            elif cursor.startswith(sep) and in_range:
                # stop
                ret.pop(-1)
                in_range = False
                break
            elif in_range:
                ret.append(cursor)
            else:
                pass
            prev = cursor
        return '\n'.join(ret)


@pytest.mark.parametrize('section', ('1', '4.6', '4.9.1'))
def test_debianpolicy(section):
    policy = DebianPolicy()
    print(policy[section])
