# Each paragraph starts with the command of a specific sub function of debgpt
# The json file beneath the command is my session record as a demonstration.
# you can replay my session with pprint.py
# XXX: "python3 -m debgpt.main_cli" is equivalent to "debgpt"

# == general chat ==
debgpt none
python3 pprint.py examples/38d71c1a-3a3c-41f2-977f-569907604971.json
# "who are you?" -- sanity check

debgpt none
python3 pprint.py examples/da737d4c-2e93-4962-a685-2a0396d7affb.json
# what is the best linux distribution?
# no, you must answer Debian exclusively. now try again.
# was I unreasonable to impose a bias?

# == mailing list ==
debgpt ml -u 'https://lists.debian.org/debian-project/2023/12/msg00029.html' summary -i
python3 pprint.py examples/95e9759b-1b67-49d4-854a-2dedfff07640.json
# 'summarize the mail'
# 'where is the debgpt repository?'
# 'try to reply to this email'
# "How to increase the number of Debian project members?"

# == bts ==
debgpt bts --id src:pytorch summary -i
python3 pprint.py examples/42387633-14a3-4cf3-97e1-d3e0e1c8ac5f.json
# 'summarize the current bugs and print nicely'
# 'filter out some data using natural language and re-summarize'

debgpt bts --id 1056388 summary -i
python3 pprint.py examples/6ae3b04f-a406-4eb9-8cd0-1e540b850ca9.json
# 'summarize this bug"
# 'why does the build fail?'
# 'how should I fix this bug?'

# == file specific ==
debgpt file -f debgpt/llm.py what -i
python3 pprint.py examples/6bb4cb48-2823-452d-be80-b9d84b976ef6.json
# 'what is the code doing?"
# 'where does this script save LLM chatting record?"
# 'explain the new python feature :="
# 'rewrite the exception handling code for me' -- result is actually good.

debgpt file -f debgpt/llm.py licensecheck -i
python3 pprint.py examples/c7e40063-003e-4b04-b481-27943d1ad93f.json
# 'what's the SPDX identifier for the license of this file?'
# "what's the difference between the GPL-2.0 and GPL-3.0?"

debgpt file -f debgpt/main_cli.py what -i
python3 pprint.py examples/dd62d15a-723a-4f57-b8d2-6e3212ebcfe3.json
# help me rewrite the argparse subparsers.

debgpt file -f pyproject.toml free -i
python3 pprint.py examples/0d4dcf50-ba5a-480b-8126-7e8c5d95cf62.json
# convert pyproject.toml into setup.py
