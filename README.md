# DebGPT -- Chatting LLM with Debian-Specific Knowledge

Large language models (LLMs) are newly emerged tools, which are capable of
handling tasks that traditional software could never achieve, such as writing
code based on the specification provided by the user. In this tool, we
attempt to experiment and explore the possibility of leveraging LLMs to aid
Debian development, in any extent.

Essentially, the idea of this tool is to gather some pieces of
Debian-specific knowledge, combine them together in a prompt, and then send
them all to the LLM. This tool provides convenient functionality for
automatically retrieving information from BTS, buildd, Debian Policy, system
manual pages, tldr manuals, Debian Developer References, etc. It also provides
convenient wrappers for external tools such as git, where debgpt can
automatically generate the git commit message and commit the changes for you.

This tool supports multiple frontends, including OpenAI and ZMQ.
The ZMQ frontend/backend are provided in this tool to make it self-contained.

1. [Install and Usage Guide (needs update)](doc/install-and-usage.md)
1. [LLM Selection and Hardware Requirements (needs update)](doc/llm-selection.md)
1. [Future Ideas (needs update)](doc/ideas.md)

## Synopsis of `debgpt` CLI


### Examples

#### Git Wrapper `debgpt git ...`

* automatically generate git commit message for staged changes, and commit them

```
debgpt git commit
```

#### Command line `debgpt --cmd ...`

* summarize the upgradable pacakges

```
debgpt -HQ --cmd 'apt list --upgradable' -A 'Briefly summarize the upgradable packages. You can categorize these packages.' -F openai --openai_model_id 'gpt-3.5-turbo-16k'
```

* auto-generate git commit message for you

```
debgpt -HQ --cmd 'git diff --staged' -A 'Briefly describe the change as a git commit message.'
```

## Proof-Of-Concept

Prompt-engineering an existing Chatting LLM with debian-specific documents,
like debian-policy, debian developer references, and some man pages.
Some examples are in [`demo.sh`](demo.sh).

The usage of LLM is limited by our imaginations. Please provide more
ideas on how we can use it.

Some imagined use cases, not yet implemented:

1. Let LLM imitate [Janitor](https://wiki.debian.org/Janitor), and possibly do some more complicated things
1. Extend Lintian with LLM for complicated checks?
1. Let LLM do mentoring (lists.debian.org/debian-mentors) e.g., reviewing a .dsc package. This is very difficult given limited context length.

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

1. `debgpt.backend` error handling ... illegal input format, overlength, CUDA OOM, etc.
4. `debgpt.llm` tune llm parameters like temperature.
5. implement very simple CoT https://arxiv.org/pdf/2205.11916.pdf
1. add perplexity API https://www.perplexity.ai
1. https://github.com/openai/chatgpt-retrieval-plugin
2. support file read range for `-f`, using `re.match(r'.+:(\d*)-(\d*)', 'setup.py:1-10').groups()`

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
