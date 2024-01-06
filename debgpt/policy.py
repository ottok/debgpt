# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import sys
import os
import re
import requests
import rich
console = rich.get_console()


class DebianPolicy(object):
    '''
    cache the plain text policy document.
    and query its sections / subsections.
    '''
    NAME = 'Debian Policy'
    URL = 'https://www.debian.org/doc/debian-policy/policy.txt'
    SEP_SECTION = '***'
    SEP_SUBSECTION = '==='
    SEP_SUBSUBSECTION = '---'

    def __init__(self, cache: str = 'policy.txt'):
        if not os.path.exists(cache):
            r = requests.get(self.URL)
            with open(cache, 'wb') as f:
                f.write(r.content)
            console.log(f'DebianPolicy> cached {self.NAME} at {cache}')
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


class DebianDevref(DebianPolicy):
    NAME = "Debian Developer's Reference"
    URL = 'https://www.debian.org/doc/manuals/developers-reference/developers-reference.en.txt'

    def __init__(self, cache: str = 'devref.txt'):
        super().__init__(cache)
