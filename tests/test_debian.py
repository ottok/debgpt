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
import pytest
from debgpt import debian


@pytest.mark.parametrize('idx', ('src:pytorch', '1056388'))
def test_debian_bts(idx: str):
    print(debian.bts(idx))


@pytest.mark.parametrize('section', ('1', '4.6', '4.6.1'))
def test_policy(section, tmp_path):
    print(debian.policy(section, debgpt_home=tmp_path))


@pytest.mark.parametrize('section', ('5.5', '1'))
def test_devref(section, tmp_path):
    print(debian.devref(section, debgpt_home=tmp_path))


@pytest.mark.parametrize('p', ('pytorch',))
def test_buildd(p):
    print(debian.buildd(p))

@pytest.mark.parametrize('url', (
    'https://lists.debian.org/debian-project/2023/12/msg00029.html',
    ))
def test_html(url):
    print(debian.html(url, raw=False))


