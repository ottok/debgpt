# Each paragraph starts with the command of a specific sub function of debgpt
# The json file beneath the command is my session record as a demonstration.
# you can replay my session with replay.py
# XXX: "python3 -m debgpt.main_cli" is equivalent to "debgpt"
# XXX: run examples/download-materials.sh first to download sample files if you want to run debgpt following these demos
# XXX: when you actually try to chat with LLM, note that the way you ask a question significant impacts the quality of the results you will get. make sure to provide as much information as possible.


# == mailing list ==
debgpt ml -u 'https://lists.debian.org/debian-project/2023/12/msg00029.html' summary
# 'summarize the mail'
# 'where is the debgpt repository?'
# 'try to reply to this email'
# "How to increase the number of Debian project members?"

# == file specific ==
debgpt file -f debgpt/llm.py what
# 'what is the code doing?"
# 'where does this script save LLM chatting record?"
# 'explain the new python feature :="
# 'rewrite the exception handling code for me' -- result is actually good.

debgpt file -f debgpt/llm.py licensecheck
# 'what's the SPDX identifier for the license of this file?'
# "what's the difference between the GPL-2.0 and GPL-3.0?"

debgpt file -f debgpt/main_cli.py what
# help me rewrite the argparse subparsers.

debgpt file -f pyproject.toml free
# convert pyproject.toml into setup.py

# == vote ==
debgpt vote -s 2023/vote_002 diff
# explain the difference between those proposals

# == man ==
debgpt man --man debhelper-compat-upgrade-checklist free  # note, this requires 40GB of CUDA memory due to manual page being too long
# what should I do to upgrade the compat from 13 to 14?

# == dev ==
debgpt x -f examples/pytorch/debian/control free
# let llm add armhf and delete kfreebsd-amd64 from architecture list

debgpt x -f examples/pytorch/debian/control --policy 7.4 free
# let llm read policy section 7.4 and modify control file to add libtorch-rocm-2.1 to Conflicts+Repalces.

debgpt x -f examples/pytorch/debian/rules --policy 4.9.1 free
# let llm help me implement the "nocheck" support in d/rules.
