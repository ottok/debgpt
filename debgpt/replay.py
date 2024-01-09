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
from rich.markup import escape
from rich.panel import Panel
import json
import argparse
import rich
console = rich.get_console()


def process_entry(entry):
    if entry['role'] == 'user':
        title = 'User Input'
        border_style = 'cyan'
    elif entry['role'] == 'assistant':
        title = 'LLM Response'
        border_style = 'green'
    elif entry['role'] == 'system':
        title = 'System Message'
        border_style = 'red'
    else:
        raise ValueError(f'unknown role in {entry}')

    panel = Panel(escape(entry['content']),
                  title=title, border_style=border_style)
    console.print(panel)


def replay(path):
    with open(path) as f:
        J = json.load(f)

    for entry in J:
        process_entry(entry)


def main():
    parser = argparse.ArgumentParser(
        description='Replay chat messages from a JSON file.')
    parser.add_argument('input_file', metavar='FILE',
                        help='JSON file containing the chat messages')
    args = parser.parse_args()
    replay(args.input_file)


if __name__ == '__main__':
    main()
