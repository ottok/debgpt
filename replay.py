# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import sys
import rich
console = rich.get_console()
import json
from rich.panel import Panel
from rich.markup import escape

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
        raise ValueError(f'unknown role')

    panel = Panel(escape(entry['content']), title=title, border_style=border_style)
    console.print(panel)

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        J = json.load(f)

    for entry in J:
        process_entry(entry)
