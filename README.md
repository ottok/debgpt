# DebGPT

A Chatting LLM with Debian-specific knowledge.

We imagine the following use cases:

1. Functionalities inheritied from the original LLM.
1. We ask the LLM to give us a patch by briefly specifiying the debian-specific changes we want to make. For instance, "add riscv64 to supported architectures".
1. We ask the LLM to generate a debian-styled response to a mail from the mailing list.
1. anything else ...

Plans:

1. Investigate the training-free prompt engineering as the proof of concept. This is easy and not hardware demanding.

## Proof-Of-Concept (Step 1 for this project)

Prompt-engineering an existing Chatting LLM with debian-specific documents, like debian-policy, debian developer references, and some man pages. Since we cannot squash all the texts into the same context due to hardware / model limits, we can wrap different prompt engineering tricks into different APIs.

Example API design can be found below. One issue is that some documents like the policy is too long. We may need to find some workarounds, or use an LLM with super large context.


```python
import debgpt
llm = debgpt.llm.from_pretrained()

# This function wraps (a part of) debian-policy document in context.
llm.ask_policy(path_of_file_or_dir_in_question, user_question)

# This function wraps (a part of) debian-devref document in context.
llm.ask_devref(path_of_file_or_dir_in_question, user_question)

# This function wraps debhelper documents (e.g., man pages) in the context.
llm.ask_dh(path_of_file_or_dir_in_question, user_question)

# This function wraps the latest sbuild buildlog at .. in the context.
llm.ask_build(user_question: str = "why did the build fail?')
```

In terms of the transformers package -- If we use a 7B LLM, 16~24GB VRAM is needed (fp16 precision). For a 13B model, it will need a 48GB GPU, or two 24GB GPUs. That said, there are other tools like https://github.com/ggerganov/llama.cpp which allows inference on CPUs (even laptops). We should write the code to dispatch to a proper inference backend.

## Dataset (Step ? far future)

1. Salsa dump
2. Debian mailing list dump

## Training (Step ? far future)

Pick an open-access LLM to fine-tune with LoRA. The concrete choise of a baseline LLM is to be investigated (e.g., should we start from pre-trained LLM or fine-tuned chatting LLM?).
The additional instruct tuning and RLHF steps are to be investigated.

## Hardware Requirement

Not estimated. But a 7B LLM is not quite difficult to deal with. According to my experience, 8xA100 GPUs must be sufficient to train.

But for proof of concept, the hardware requirement should be lower.

## References

1. https://lists.debian.org/debian-project/2023/12/msg00028.html
2. LoRA paper
3. InstructGPT paper

## License

MIT/Expat
