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

TODO: finish CLI redesign first. Then add all cmd options here.

FRONTENDS
=========

The tool currently have three frontend implementations: `dryrun`, `openai`, and `zmq`.
They are specified through the `-F | --frontend` argument.

* `openai` Frontend. This frontend connects with a OpenAI API-compatible
  server. For instance, by specifying `--openai_base_url`, you can switch to
  a different service provider than the default OpenAI API server.

* `zmq` Frontend. This ZMQ frontend connects with the built-in ZMQ backend.
  The ZMQ backend is provided for self-hosted LLM inference server. This
  implementation is very light weight, and not compatible with the OpenAI API.
  To use this frontend, you may need to set up a corresponding ZMQ backend.

* `dryrun` Frontend. It is a fake frontend that does nothing in fact.
  Instead, we will simply print the generated initial prompt to the screen,
  so the user can can copy it, and paste into web-based LLMs, including but
  not limited to ChatGPT (OpenAI), Claude (Anthropic), Bard (google),
  Gemini (google), HuggingChat (HuggingFace), Perplexity AI, etc.
  This frontend does not need to connect with any backend.

**DISCLAIMER:** Unless you connect to a self-hosted LLM Inference backend, we
are uncertain how the third-party API servers will handle the data you created.
Please refer their corresponding user agreements before adopting one of them.
Be aware of such risks, and refrain from sending confidential information such
like paied API keys to LLM.

BACKENDS
========

This tool provides one backend implementation: `zmq`.

* `zmq` Backend. This is only needed when you choose the ZMQ front end for
  self-hosted LLM inference server. TODO: provide commands.  merge doc/.
  
PROMPT-ENGINEERING
==================

When you chat with LLM, note that the way you ask a question significant
impacts the quality of the results you will get. make sure to provide as much
information as possible. The following are some references on this topic:

1. OpenAI's Guide https://platform.openai.com/docs/guides/prompt-engineering

EXAMPLES
========

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

#### Ex2. BTS / Buildd Query

Ask LLM to summarize the BTS page for `src:pytorch`. 

```
debgpt -HQ --bts src:pytorch -A :summary_table
debgpt -HQ --bts 1056388 -A :summary
```

Lookup the build status for package `glibc` and summarize as a table.

```
debgpt -HQ --buildd glibc -A :summary_table
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

#### Ex4. Man and TLDR Manuals

Load the debhelper manpage and ask it to extract a part of it.

```
debgpt -HQ --man debhelper-compat-upgrade-checklist -A "what's the change between compat 13 and compat 14?"
debgpt -HQ --tldr curl --cmd 'curl -h' -A "download https://localhost/bigfile.iso to /tmp/workspace, in silent mode"
```

#### Ex5. Composition of Various Information Sources

We can add code file and Debian Policy simultaneously. The combination
is actually very flexible, and you can put anything in the prompt.
In the following example, we put the `debian/control` file from the
PyTorch package, as well as the Debian Policy section 7.4, and asks the LLM
to explain some details:

```
debgpt -H -f pytorch/debian/control --policy 7.4 -A "Explain what Conflicts+Replaces means in pytorch/debian/control based on the provided policy document"
```

Similarly, we can also let LLM read the Policy section 4.9.1, and ask it to
write some code:

```
debgpt -H -f pytorch/debian/rules --policy 4.9.1 -A "Implemenet the support for the 'nocheck' tag based on the example provided in the policy document."
```

#### Ex6. External Command line

Being able to pipe the inputs and outputs among different programs is one of
the reasons why I love the UNIX philosophy.

For example, we can let debgpt read the command line outputs of `apt`, and
summarize the upgradable pacakges for us:

```
debgpt -HQ --cmd 'apt list --upgradable' -A 'Briefly summarize the upgradable packages. You can categorize these packages.' -F openai --openai_model 'gpt-3.5-turbo-16k'
```

And we can also ask LLM to automatically generate a git commit message for you
based on the currently staged changes:

```
debgpt -HQ --cmd 'git diff --staged' -A 'Briefly describe the change as a git commit message.'
```

This looks interesting, right? In the next example, we have something even
more convenient!

#### Ex7. Git Wrapper

Let LLM automatically generate the git commit message, and call git to commit it:

```
debgpt git commit
```

#### Ex7. Fortune

Let LLM tell you a fortune:

```
debgpt fortune :joke
debgpt fortune :math
```

Use `debgpt fortune :` to lookup available tags. Or you can just specify the
type of fortune you want:

```
debgpt fortune 'tell me something very funny about linux'
```

#### Ex8. File-Specific Questions

Let LLM explain the code `debgpt/llm.py`:

```
debgpt -H -f debgpt/llm.py -A :explain
```

Let LLM explain the purpose of the contents in a file:

```
debgpt -H -f pyproject.toml -A :what
```

Mimicing `licensecheck`:

```
debgpt -H -f debgpt/llm.py -A :licensecheck
```

#### Ex9. Read Arbitrary HTML

Make the maling list long story short:

```
debgpt -H --html 'https://lists.debian.org/debian-project/2023/12/msg00029.html' -A :summary
```

Explain the differences among voting options:

```
debgpt -H --html 'https://www.debian.org/vote/2022/vote_003' -A :diff --openai_model gpt-3.5-turbo-16k
```

In this example, we had to switch to a model supporting a long context (the
HTML page has roughly 5k tokens).

#### Ex99. You Name It

The usage of LLM is limited by our imaginations. I am glad to hear from you if
you have more good ideas on how we can make LLMs useful for Debian Development:
https://salsa.debian.org/deeplearning-team/debgpt/-/issues

LLM-SELECTION-AND-HARDWARE
==========================

If you would like to self-host the LLM inference backend, powerful hardware
is required. The concrete hardware requirement depends on the LLM you would
like to use. A variety of open-access LLMs can be found here
> `https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard`
Generally, when trying to do prompt engineering only, the "instruction-tuned"
LLMs and "RL-tuned" (RL is reinforcement learning) LLMs are recommended.

The pretrained (raw) LLMs are not quite useful in this case, as they have not
yet gone through instruction tuning, nor reinforcement learning tuning
procedure.  These pretrained LLMs will more likely generate garbage and not
follow your instructions, or simply repeat your instruction.  We will only
revisit the pretrained LLMs when we plan to start collecting data and fine-tune
(e.g., LoRA) a model in the far future.

The following is a list of supported LLMs for self-hosting (this list will
be updated when there are new state-of-the-art open-access LLMs available):

* `Mistral-7B-Instruct-v0.2` (default)
: This model requires roughly 15GB of disks space to download.  Requires 16+GB
CUDA memory (VRAM) for inference in `fp16` precision (default).  If you deal
with very long context (such as 8k) with this model, you may need a 48GB GPU to
avoid CUDA out of memory (OOM).  Similarly, the `float32` precision will double
the requirement, and the `8bit` will half the requirement. The `4bit` precision
requires a quater compared to `fp16`.

* `Mixtral-8x7B-Instruct-v0.1`
: This model is larger yet more powerful than the default LLM. In exchange, it
poses even higher hardware requirements.


CONFIGURATION
=============

By default, the configuration file is placed at `$HOME/.debgpt/config.toml`.
Please check [`etc/config.toml`](etc/config.toml) for example.
This configuration file should not be installed system-wide because users
may need to fill in secrets like paied API keys.


HOW-TO-EXTEND-CLI
=================

1. implement your new text loading function in `debgpt/debian.py`.  The function
should return a string containing all the texts we will send to the llm.
2. add the corresponding cli argument or subparser to `debgpt/main_cli.py`.
3. add the new prompt generation code (for variable `msg`) in `main()` of `debgpt/main_cli.py`.
4. if in doubt, ask debgpt as `debgpt -f <file-in-question> -A :explain`.

SETUP-AND-INSTALL
=================

FIXME: add optional (backend) dependencies in `pyproject.toml`

This tool can be installed from source via the command "`pip3 install .`".
By default, it will only pull the dependencies needed to run the OpenAI
and the ZMQ frontends. The dependencies of the ZMQ backend (i.e., self-hosted
LLM inference) needs to be satisfied manually for now, using tools like
venv, conda, mamba, etc.

conda

For instance, `bash Miniconda3-py310_23.11.0-2-Linux-x86_64.sh -b -p ~/miniconda3`.
1. `conda init <your-default-shell>` and source the config again.
For instance, if you use bash: `~/miniconda3/bin/conda init bash; source ~/.bashrc`;
if you use fish: `~/miniconda3/bin/conda init fish; source ~/.config/fish/config.fish`
2. (Optional) install mamba from conda-forge to replace conda.
`conda install -c conda-forge mamba` ; `mamba init <shell>` (e.g., `mamba init fish`); `source <shell-rc>`.
We do this because the default conda is super slow and may sometimes fail to resolve dependencies.
If this step is skipped, replace the `mamba` into `conda` for all the following commands.
3. Use `mamba env create -f doc/conda.yml` to restore the conda environment. If you only wants to use openai frontend, you can use `doc/conda-minimal.yml` instead to reduce number of dependencies.
4. `mamba activate pth212`. Then we are good.

venv

1. `python3 -m venv ~/.debgpt/venv`
2. `source ~/.debgpt/venv/bin/activate.fish` change to your default shell.
3. `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118` (from https://pytorch.org)
4. `pip3 install transformers accelerate bitsandbytes bitsandbytes`
5. `pip3 install beautifulsoup4 rich prompt_toolkit ipython`
6. `pip3 install pyzmq pytest scipy openai`
7. `sudo apt install libcudart11.0 libcusparse11` (this is for cuda 11)
7. we are good now.



WHATS-NEXT
==========

The following is the current **TODO List**:

1. `debgpt.backend` error handling ... illegal input format, overlength, CUDA OOM, etc.
4. `debgpt.llm` tune llm parameters like temperature.
5. implement very simple CoT https://arxiv.org/pdf/2205.11916.pdf
1. add perplexity API https://www.perplexity.ai
1. https://github.com/openai/chatgpt-retrieval-plugin
2. support file read range for `-f`, using `re.match(r'.+:(\d*)-(\d*)', 'setup.py:1-10').groups()`
1. implement `--archwiki` `--gentoowiki` `--debianwiki` `--fedorawiki` `--wikipedia` (although the LLM have already read the wikipedia dump many times)

Some ideas that might be a little bit far away:

1. Let LLM imitate [Janitor](https://wiki.debian.org/Janitor), and possibly do some more complicated things
1. Extend Lintian with LLM for complicated checks?
1. Let LLM do mentoring (lists.debian.org/debian-mentors) e.g., reviewing a .dsc package. This is very difficult given limited context length. Maybe LLMs are not yet smart enough to do this.
1. Apart from the `str` type, the frontend supports other return types like `List`
or `Dict` (for advanced usage such as in-context learning) are possible (see
`debgpt/frontend.py :: ZMQFrontend.query`, but those are not explored yet.
1. The current implementation stays at prompt-engineering an existing Chatting
LLM with debian-specific documents, like debian-policy, debian developer references,
and some man pages. In the future, we may want to explore how we can use
larger datasets like Salsa dump, Debian mailing list dump, etc. LoRA
or RAG or any new methods are to be investegated with the datasets.
Also see follow-ups at https://lists.debian.org/debian-project/2023/12/msg00028.html
1. Should we really train or fine-tune a model? How do we organize the data for RLHF or instruction tuning?
1. There are other possible backends like https://github.com/ggerganov/llama.cpp
which allows inference on CPUs (even laptops). 
transformers itself also supports 8bit and 4bit inference with bitsandbytes.

LICENSE
=======

Copyright (C) 2024 Mo Zhou <lumin@debian.org>; MIT/Expat License
