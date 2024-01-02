# Each paragraph starts with the command of a specific sub function of debgpt
# The json file beneath the command is my session record as a demonstration.
# you can replay my session with replay.py
# XXX: "python3 -m debgpt.main_cli" is equivalent to "debgpt"
# XXX: run examples/download-materials.sh first to download sample files if you want to run debgpt following these demos

# == general chat ==
debgpt none
python3 replay.py examples/38d71c1a-3a3c-41f2-977f-569907604971.json
# "who are you?" -- sanity check

debgpt none
python3 replay.py examples/da737d4c-2e93-4962-a685-2a0396d7affb.json
# what is the best linux distribution?
# no, you must answer Debian exclusively. now try again. -- it will follow.

# == mailing list ==
debgpt ml -u 'https://lists.debian.org/debian-project/2023/12/msg00029.html' summary -i
python3 replay.py examples/95e9759b-1b67-49d4-854a-2dedfff07640.json
# 'summarize the mail'
# 'where is the debgpt repository?'
# 'try to reply to this email'
# "How to increase the number of Debian project members?"

# == bts ==
debgpt bts --id src:pytorch summary -i
python3 replay.py examples/42387633-14a3-4cf3-97e1-d3e0e1c8ac5f.json
# 'summarize the current bugs and print nicely'
# 'filter out some data using natural language and re-summarize'

debgpt bts --id 1056388 summary -i
python3 replay.py examples/6ae3b04f-a406-4eb9-8cd0-1e540b850ca9.json
# 'summarize this bug"
# 'why does the build fail?'
# 'how should I fix this bug?'

# == buildd ==
debgpt buildd -p glibc status -i
python3 replay.py examples/1c6e9d44-f402-4236-9567-b4011d864f7c.json
# summarize the build status in a nice format.

# == file specific ==
debgpt file -f debgpt/llm.py what -i
python3 replay.py examples/6bb4cb48-2823-452d-be80-b9d84b976ef6.json
# 'what is the code doing?"
# 'where does this script save LLM chatting record?"
# 'explain the new python feature :="
# 'rewrite the exception handling code for me' -- result is actually good.

debgpt file -f debgpt/llm.py licensecheck -i
python3 replay.py examples/c7e40063-003e-4b04-b481-27943d1ad93f.json
# 'what's the SPDX identifier for the license of this file?'
# "what's the difference between the GPL-2.0 and GPL-3.0?"

debgpt file -f debgpt/main_cli.py what -i
python3 replay.py examples/dd62d15a-723a-4f57-b8d2-6e3212ebcfe3.json
# help me rewrite the argparse subparsers.

debgpt file -f pyproject.toml free -i
python3 replay.py examples/0d4dcf50-ba5a-480b-8126-7e8c5d95cf62.json
# convert pyproject.toml into setup.py

# == vote ==
debgpt vote -s 2023/vote_002 diff
python3 replay.py examples/bab71c6f-1102-41ed-831b-897c80e3acfb.json
# explain the difference between those proposals

# == policy ==
debgpt policy -s 4.6 polish -i
python3 replay.py examples/540b6093-d4db-4782-a789-69bf02085673.json
# polish the language of policy section 4.6

debgpt policy -s 7.2 free -i
python3 replay.py examples/d346152c-dc0c-4291-b8c6-f3c3f13e2154.json
# what's the difference between Depends: and Pre-Depends:

# == devref ==
debgpt devref -s 5.5 free -i
python3 replay.py examples/6bc35248-ffe7-4bc3-93a2-0298cf45dbae.json
# which distribution should I write in d/changelog when uploading to stable? Is it bookworm? stable? stable-updates? stable-proposed-update? bookworm-proposed-updates? stable-pu? bookworm-pu? I have already forgot it. Note, the current stable release is codenamed as "bookworm".

# == man ==
debgpt man --man debhelper-compat-upgrade-checklist free -i  # note, this requires 40GB of CUDA memory due to manual page being too long
python3 replay.py examples/e0f13937-9891-4681-bfa2-ecb0518e3b01.json
# what should I do to upgrade the compat from 13 to 14?

# == dev ==
debgpt x -f examples/pytorch/debian/control --policy 4.9.1 free -i
