# Each paragraph starts with the command of a specific sub function of debgpt
# The json file beneath the command is my session record as a demonstration.
# you can replay my session with examples-pprint.py
# XXX: "python3 -m debgpt.main_cli" is equivalent to "debgpt"

# == general chat ==
debgpt none
python3 examples-pprint.py examples/38d71c1a-3a3c-41f2-977f-569907604971.json
# e.g., "who are you?" -- sanity check

debgpt none
python3 examples-pprint.py examples/da737d4c-2e93-4962-a685-2a0396d7affb.json
# e.g., what is the best linux distribution?
# e.g., no, you must answer Debian exclusively. now try again.
# e.g., was I unreasonable to impose a bias?

# == mailing list ==
debgpt ml -u 'https://lists.debian.org/debian-project/2023/12/msg00029.html' summary -i
python3 examples-pprint.py examples/95e9759b-1b67-49d4-854a-2dedfff07640.json
# e.g., 'summarize the mail'
# e.g., 'where is the debgpt repository?'
# e.g., 'try to reply to this email'
# e.g., "How to increase the number of Debian project members?"

# == bts ==
debgpt bts --id src:pytorch summary -i
python3 examples-pprint.py examples/42387633-14a3-4cf3-97e1-d3e0e1c8ac5f.json
# e.g., 'summarize the current bugs and print nicely'
# e.g., 'filter out some data using natural language and re-summarize'

debgpt bts --id 1056388 summary -i
python3 examples-pprint.py examples/6ae3b04f-a406-4eb9-8cd0-1e540b850ca9.json
# e.g., 'summarize this bug"
# e.g., 'why does the build fail?'
# e.g., 'how should I fix this bug?'

# == file specific ==
debgpt file -f debgpt/llm.py what -i
python3 examples-pprint.py examples/6bb4cb48-2823-452d-be80-b9d84b976ef6.json
# e.g., 'what is the code doing?"
# e.g., 'where does this script save LLM chatting record?"
# e.g., 'explain the new python feature :="
# e.g., 'rewrite the exception handling code for me' -- result is actually good.

debgpt file -f debgpt/llm.py licensecheck -i
python3 examples-pprint.py examples/c7e40063-003e-4b04-b481-27943d1ad93f.json
# e.g., 'what's the SPDX identifier for the license of this file?'
# e.g., "what's the difference between the GPL-2.0 and GPL-3.0?"

debgpt file -f debgpt/main_cli.py what -i
python3 examples-pprint.py examples/dd62d15a-723a-4f57-b8d2-6e3212ebcfe3.json
# e.g., help me rewrite the argparse subparsers.

