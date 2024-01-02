# LLM Selection and Hardware Requirement

A variety of open-access LLMs can be found here https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard

When we are trying to do prompt engineering only, the instruction-tuned LLMs and RL-tuned LLMs are preferred.
The pretrained (raw) LLMs are not quite useful in this case, as they have not yet gone through instruction tuning, nor reinforcement learning tuning procedure).
We will only revisit the pretrained LLMs when we plan to start collecting data and fine-tune (e.g., LoRA) a model in the far future.

In the current implementation, we use `Mistral-7B-Instruct-v0.2`.
We may switch to other LLMs in the future.

*Candidates:*

1. https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1
1. https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
1. LLAMA-2 https://huggingface.co/meta-llama


## Hardware Limitations

* `Mistral-7B-Instruct-v0.2`: roughly 15GB disk space to store the weights.
Requires 16+GB CUDA memory for inference in float16 precision.
If using float32 precision, you will need 32+GB CUDA memory.
Eligible GPUs are, for example, Nvidia RTX3090, RTX4090, RTX A5000, or better GPUs.
Its maximum context length is reportedly 8k. But a 48GB GPU will end up with CUDA OOM before we reach that length.

* Training/Fine-tuning:
Not estimated. According to my experience, 8xA100 GPUs must be sufficient to
train a 7B model.  LoRA or RAG should require less than that.

For a 13B model, it will need a 48GB GPU, or two 24GB GPUs.

## Inference Software

There are other tools like https://github.com/ggerganov/llama.cpp
which allows inference on CPUs (even laptops). 
transformers itself also supports 8bit and 8bit inference with bitsandbytes.
Currently we stick to transformers for simplicity.

## Safety/Security Guideline

Direct internet access is not allowed for LLM.
We can download internet contents with trusted tool first.

LLM's local file read permission should be explicitly approved by user.
We read local files using trusted way, then feed the contents to LLM.
