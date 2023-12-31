# DebGPT

A Chatting LLM with Debian-specific knowledge.

We imagine the following use cases:

1. Functionalities inheritied from the original LLM.
1. We ask the LLM to give us a patch by briefly specifiying the debian-specific changes we want to make. For instance, "add riscv64 to supported architectures".
1. We ask the LLM to generate a debian-styled response to a mail from the mailing list.
1. anything else ...

## Dataset

1. Salsa dump
2. Debian mailing list dump

## Training

Pick an open-access LLM to fine-tune with LoRA. The concrete choise of a baseline LLM is to be investigated (e.g., should we start from pre-trained LLM or fine-tuned chatting LLM?).
The additional instruct tuning and RLHF steps are to be investigated.

## Hardware Requirement

Not estimated. But a 7B LLM is not quite difficult to deal with. According to my experience, 8xA100 GPUs must be sufficient to deal with it.

## References

1. https://lists.debian.org/debian-project/2023/12/msg00028.html
2. LoRA paper
3. InstructGPT paper

## License

GPL-2.0+
