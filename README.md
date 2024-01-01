# DebGPT -- Chatting LLM with Debian-specific knowledge

Large language models (LLMs) are newly emerged tools, which are capable of
handling tasks that traditional software could never achieve, such as writing
code based on the specification provided by the user. However, Debian-specific
knowledge is a kind of niche knowledge, which is not learnt well by commercial
or open-access LLMs. In this project, we attempt to explore the possibility
of leveraging LLMs to aid Debian development, in any extent.

*Status:* proof-of-concept (prompt engineering existing LLMs and wrap it with a set of API)

*Discussions:* Open an issue for this repo.

*Mailing-List:* Debian Deep Learning Team <debian-ai@lists.debian.org>

## Proof-Of-Concept (Step 1 for this project)

This step is easy. Does not require any model parameter updates.

Prompt-engineering an existing Chatting LLM with debian-specific documents, like debian-policy, debian developer references, and some man pages.
Since we cannot squash all the texts into the same context due to hardware / model limits, we can wrap different prompt engineering tricks into different APIs.

The imagined use cases will be like the follows:


```python
import debgpt
llm = debgpt.llm.from_pretrained()

# The general function just calls the plain LLM backend.
llm.ask(user_question)
#   e.g. "who are you?" -- sanity check

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

# This leverages LLM's capability for summarizing texts.
llm.bts(bts_number: int, user_question)
#   e.g.: "briefly summarize it."

# Let LLM do the development work, and generates a patch for you
llm.dev(path_of_file_or_dir, user_question, *, inplace:bool=False)
#   e.g., debian/control, "add riscv64 to supported architectures".

# Let LLM behave like a human (it is not good at this)
llm.reply_mail(debian_bts_or_ml_html_link, user_question:str=None)
```

Command line interfaces

```shell
$ python3 -m debgpt.backend           # server
$ python3 -m debgpt.frontend          # client
$ debgpt                              # client shortcut
```

## TODOs

1. separate the frontend (user cli, sends llm query, and receives llm response, and possibly execute LLM generated code) and backend (LLM inference, exposed through zmq). This is postponed after poc stage.

## LLM Selection

Nore certain. But we shall grab one with good performance, and allows free commercial usage (or more permissive ones)

https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard

Instruction-tuned and RL-tuned LLMs are preferred. Do not try pretrained raw LLMs -- they are not useful here.
The pretrained (raw) LLMs and the fine-tuned LLMs (without instruction tuning or RL tuning) are only useful when we plan to collect debian-specific data and fine-tune the model.

*Candidates:*

1. https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1
1. https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
1. LLAMA-2 https://huggingface.co/meta-llama


## Evaluations

### [Janitor](https://wiki.debian.org/Janitor) Tasks

Janitor tasks are not quite sophisticated for LLM. These tasks can be used as sanity checks.

### More complicated tasks

Depends on your imagination.

## Hardware/Software Limitations

Not estimated. But a 7B LLM is not quite difficult to deal with. According to
my experience, 8xA100 GPUs must be sufficient to train a full 7B model.
LoRA or RAG should require much less than that.

One potential issue is that some documents like the policy is too long. We may
need to find some workarounds, or use an LLM with super large context.  In
terms of the transformers package -- If we use a 7B LLM, 16~24GB VRAM is needed
(fp16 precision). For a 13B model, it will need a 48GB GPU, or two 24GB GPUs.
That said, there are other tools like https://github.com/ggerganov/llama.cpp
which allows inference on CPUs (even laptops). We should write the code to
dispatch to a proper inference backend.

Internet access is not allowed for LLM.
LLM's file read permission should be explicitly approved by user.

## Future Explorations

### Dataset (Step ? far future)

1. Salsa dump
2. Debian mailing list dump

### Training (Step ? far future)

Pick an open-access LLM to fine-tune with LoRA. The concrete choise of a baseline LLM is to be investigated (e.g., should we start from pre-trained LLM or fine-tuned chatting LLM?).
The additional instruct tuning and RLHF steps are to be investigated.

Possible solutions

1. LoRA

2. RAG

## References

1. https://lists.debian.org/debian-project/2023/12/msg00028.html
2. LoRA paper
3. InstructGPT paper

## License

MIT/Expat
