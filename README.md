# DebGPT -- Chatting LLM with Debian-Specific Knowledge

Large language models (LLMs) are newly emerged tools, which are capable of
handling tasks that traditional software could never achieve, such as writing
code based on the specification provided by the user. However, Debian-specific
knowledge is a kind of niche knowledge, which is not learnt well by commercial
or open-access LLMs. In this project, we attempt to explore the possibility
of leveraging LLMs to aid Debian development, in any extent.

*Status:* proof-of-concept (prompt engineering existing LLMs and wrap it with a set of API)

*Discussions:* Open an issue for this repo.

*Mailing-List:* Debian Deep Learning Team <debian-ai@lists.debian.org>

*Technical-Details:*

1. [Python Environment Setup Guide](doc/install.md)
1. [Usage Instructions](doc/usage.md)
1. [LLM Selection and Hardware Requirements](doc/llm-selection.md)
1. [Future Ideas](doc/ideas.md)

## Proof-Of-Concept

Prompt-engineering an existing Chatting LLM with debian-specific documents,
like debian-policy, debian developer references, and some man pages.

The examples included in [`demo.sh`](demo.sh) are already run-able.
The contents of this script are also shown below.
I uploaded my LLM session of each command in the `examples/` directory.
You can use [`examples-pprint.py`](examples-pprint.py) to reply these sessions.

The usage of LLM is limited by our imaginations. Please provide more
ideas on how we can use it.

Some imagined use cases, not yet implemented:


```python
# This function wraps (a part of) debian-policy document in context.
llm.ask_policy(path_of_file_or_dir, user_question)
#   e.g. debian/control, "what's the difference between Depends: and Pre-Depends: ?"

# This function wraps (a part of) debian-devref document in context.
llm.ask_devref(path_of_file_or_dir, user_question)
#   e.g., debian/changelog, "what is the correct release name when I prepare the upload for Debian stable? bookworm? stable? bookworm-proposed-updates? or anything else?"

# This function wraps debhelper documents (e.g., man pages) in the context.
llm.ask_dh(path_of_file_or_dir, user_question)
#   e.g., debian/control, "what is the correct way to specify debhelper dependency with compat level 13?"

# This function wraps the latest sbuild buildlog at .. in the context.
llm.ask_build(user_question)
#   e.g.: "why does the build fail?'

# Let LLM do the development work, and generates a patch for you
llm.dev(path_of_file_or_dir, user_question, *, inplace:bool=False)
#   e.g., debian/control, "add riscv64 to supported architectures".

# Let LLM summarize voting information (vote.debian.org)
llm.vote(vote_id, user_question)
#   XXX: raise a warning and highlight it in red. This is sensitive. Do not make your vote decision based on LLM's outputs.
#   e.g., xxx, "explain the difference between different proposals."

# Let LLM do mentoring (lists.debian.org/debian-mentors)
llm.mentor(maling-list-html)
#   e.g., for reviewing a .dsc package. This is difficult for LLM.

# Let LLM imitate [Janitor](https://wiki.debian.org/Janitor), and possibly do
# some more complicated things
```

## Infrastructure

I don't know how many DDs will be interested in this if it works well.
Based on the number of DD users, as well as LLM's actual usefulness, we might work with the infrastructure team to setup a LLM inference server to run the backend.

## License

```
Copyright (C) 2024 Mo Zhou <lumin@debian.org>
MIT/Expat
```
