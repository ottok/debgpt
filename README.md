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

1. [Install and Usage Guide](doc/install-and-usage.md)
1. [LLM Selection and Hardware Requirements](doc/llm-selection.md)
1. [Future Ideas](doc/ideas.md)

## Proof-Of-Concept

Prompt-engineering an existing Chatting LLM with debian-specific documents,
like debian-policy, debian developer references, and some man pages.

The examples included in [`demo.sh`](demo.sh) are already run-able.
The contents of this script are also shown below.
I uploaded my LLM session of each command in the `examples/` directory.
You can use [`replay.py`](replay.py) to reply these sessions.

The usage of LLM is limited by our imaginations. Please provide more
ideas on how we can use it.

Some imagined use cases, not yet implemented:

1. Let LLM imitate [Janitor](https://wiki.debian.org/Janitor), and possibly do some more complicated things
1. Extend Lintian with LLM for complicated checks?
1. Let LLM do mentoring (lists.debian.org/debian-mentors) e.g., reviewing a .dsc package. This is very difficult given limited context length.


```python
# Let LLM do the development work, and generates a patch for you
llm.dev(path_of_file_or_dir, user_question, *, inplace:bool=False)
#   e.g., debian/control, "add riscv64 to supported architectures".
```

## How to extend the CLI

1. implement your new prompt generator in `debgpt/debian.py`.  The function
should return a string containing all the texts we will send to the llm.  Some
other return types like `List` or `Dict` (for advanced usage such as in-context
learning) are possible (see `debgpt/frontend.py :: ZMQFrontend.query`, but
those are not explored yet.
2. add the corresponding cli argument subparser to `debgpt/main_cli.py`.
3. add the new prompt generation code (for variable `msg`) in `main()` of `debgpt/main_cli.py`.
4. if in doubt, ask debgpt as `debgpt file -f <file-in-question> what -i`.

## TODO List

1. `debgpt.backend` error handling ... illegal input format, overlength, etc.
2. `debgpt.llm` support 8bit and 4bit inference (cpu)
3. `debgpt.frontend` implement the frontend instance using OpenAI API.
4. `debgpt.llm` tune llm parameters like temperature.

## Infrastructure

I don't know how many DDs will be interested in this if it works well.  Based
on the number of DD users, as well as LLM's actual usefulness, we might work
with the infrastructure team to setup a LLM inference server to run the
backend.

Or, alternatively, we can subscribe the commercial LLM API for the organization
(to integrate into infrastructure), or for the individuals (for development
work, as a part of debian member benefit) with debian funding if it turns to be
really useful to people. The commercial LLMs supports much longer context
length than the one we hosted locally, and they are backed by strong hardware.
With the subscription, we can implement a new frontend using the commercial
API.

I have not talked with the leader about any of these yet.

## License

```
Copyright (C) 2024 Mo Zhou <lumin@debian.org>
MIT/Expat
```
