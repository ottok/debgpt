# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
import sys
import rich
console = rich.get_console()
import json
from rich.panel import Panel
from rich.markup import escape

with open(sys.argv[1]) as f:
    J = json.load(f)

for entry in J:
    if entry['role'] == 'user':
        title = 'User Input'
    elif entry['role'] == 'assistant':
        title = 'LLM Response'

    panel = Panel(escape(entry['content']), title=title)
    console.print(panel)
