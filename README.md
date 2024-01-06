% DebGPT(1) | Chatting LLM with Debian-Specific Knowledge
% Copyright (C) 2024 Mo Zhou <lumin@debian.org>; MIT License.

NAME
====

DebGPT - Chatting LLM with Debian-Specific Knowledge

> "AI" = "Artificial Idiot"


SYNOPSIS
========

`debgpt [-h] [--quit] [--multiline] [--hide_first] [--verbose] [--output OUTPUT] [--version] [--debgpt_home DEBGPT_HOME]
      [--frontend {dryrun,zmq,openai}] [--temperature TEMPERATURE] [--top_p TOP_P] [--openai_base_url OPENAI_BASE_URL]
      [--openai_api_key OPENAI_API_KEY] [--openai_model OPENAI_MODEL] [--zmq_backend ZMQ_BACKEND] [--bts BTS] [--bts_raw] [--cmd CMD]
      [--buildd BUILDD] [--file FILE] [--policy POLICY] [--devref DEVREF] [--tldr TLDR] [--ask ASK]
      [SUBCOMMAND] ...`

DESCRIPTION
===========

*This tool is currently experimental.*

Large language models (LLMs) are newly emerged tools, which are capable of
handling tasks that traditional software could never achieve, such as writing
code based on the specification provided by the user. With this tool, we
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

OPTIONS
=======

`-h, --help`
: show this help message and exit

`--cmd CMD`
: add the command line output to the prompt


```
options:
  --quit, -Q            directly quit after receiving the first response from LLM, instead of staying in interation.
  --multiline, -M       enable multi-line input for prompt_toolkit. use Meta+Enter to accept the input instead.
  --hide_first, -H      hide the first (generated) prompt; do not print argparse results
  --verbose, -v         verbose mode. helpful for debugging
  --output OUTPUT, -o OUTPUT
                        write the last LLM message to specified file
  --version             show DebGPT software version and quit.
  --debgpt_home DEBGPT_HOME
                        directory to store cache and sessions.
  --frontend {dryrun,zmq,openai}, -F {dryrun,zmq,openai}
  --temperature TEMPERATURE, -T TEMPERATURE
                        Sampling temperature. Typically ranges within [0,1]. Low values like 0.2 gives more focused (coherent) answer. High values like
                        0.8 gives a more random (creative) answer. Not suggested to combine this with with --top_p. See
                        https://platform.openai.com/docs/api-reference/chat/create
  --top_p TOP_P, -P TOP_P
  --openai_base_url OPENAI_BASE_URL
  --openai_api_key OPENAI_API_KEY
  --openai_model OPENAI_MODEL
  --zmq_backend ZMQ_BACKEND
                        the ZMQ frontend endpoint
  --bts BTS             Retrieve BTS webpage to prompt. example: "src:pytorch", "1056388"
  --bts_raw             load raw HTML instead of plain text.
  --buildd BUILDD       Retrieve buildd page for package to prompt.
  --file FILE, -f FILE  load specified file(s) in prompt
  --policy POLICY       load specified policy section(s). (e.g., "1", "4.6")
  --devref DEVREF       load specified devref section(s).
  --tldr TLDR           add tldr page to the prompt.
  --ask ASK, -A ASK     Question template to append at the end of the prompt. Specify ':' for printing all available templates. Or a customized string not
                        starting with the colon.

```

```
positional arguments:
  {backend,git,replay,stdin,ml,file,vote,man,dev,x}
                        specific task handling
    backend             start backend server (self-hosted LLM inference)
    git                 git command wrapper
    replay              replay a conversation from a JSON file
    stdin               read stdin, print response and quit.
    ml                  mailing list
    file                ask questions regarding a specific file
    vote                vote.debian.org
    man                 manual page
    dev (x)             code editing with context
```


### Examples

The following examples are roughly organized in the order of complexity of command line.

#### Ex1. General Chat

When no arguments are given, `debgpt` degenerates into a general terminal
chatting client with LLM backends. Use `debgpt -h` to see detailed usage.

```
debgpt
```

If you want to quit (`-Q`) after receiving the first response from LLM regarding the question (`-A`):

```
debgpt -Q -A "who are you?"
```

After each session, the chatting history will be saved in `~/.debgpt` as a
json file in a unique name.  You can use `debgpt replay <file_name>` to replay the history.

#### Ex2. BTS Query

Ask LLM to summarize the BTS page for `src:pytorch`. 

```
debgpt -HQ --bts src:pytorch -A :summary_table
debgpt -HQ --bts 1056388 -A :summary
```

When the argument to `-A/--ask` is a tag starting with a colon sign `:`, such
as `:summary`, it will be automatically replaced into a default question
template. Use `debgpt -A :` to lookup available templates.

The `-H` argument will skip printing the first prompt generated by `debgpt`,
because it is typically very lengthy, and people may not want to read it.

#### Ex3. Debian Policy and Developer References

Load a section of debian policy document, such as section "4.6", and ask a question

```
debgpt -H --policy 7.2 -A "what is the difference between Depends: and Pre-Depends: ?"
debgpt -H --devref 5.5 -A :summary
```

#### Ex4. Buildd Query

Lookup the build status for package `glibc` and summarize as a table.

```
debgpt -HQ --buildd glibc -A :summary_table
```

#### Ex1. Git Wrapper `debgpt git ...`

* automatically generate git commit message for staged changes, and commit them

```
debgpt git commit
```

#### Ex2. External Command line `debgpt --cmd ...`

* summarize the upgradable pacakges

```
debgpt -HQ --cmd 'apt list --upgradable' -A 'Briefly summarize the upgradable packages. You can categorize these packages.' -F openai --openai_model 'gpt-3.5-turbo-16k'
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
1. add man page for `debgpt`

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
