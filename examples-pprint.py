import sys
import rich
console = rich.get_console()
import json
from rich.panel import Panel

with open(sys.argv[1]) as f:
    J = json.load(f)

for entry in J:
    if entry['role'] == 'user':
        title = 'User Input'
    elif entry['role'] == 'assistant':
        title = 'LLM Response'

    panel = Panel(entry['content'], title=title)
    console.print(panel)
