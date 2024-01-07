# Setup / Install Instructions

If you plan to use the `openai` frontend, there is no hardware requirement and
you can skip the following hardware requirement part.  But if you plan to use
the `zmq` frontend with self-hosted LLM backend, specific hardware is
necessary.

## Hardware requirement (if you want to self-host LLM backend)

The default step (for self-hosted LLM backend) requires a nvidia driver that
supports at least CUDA 11.8. The default LLM is `Mistral7B`, which takes roughly
15GB disk space. The `Mixtral8x7B` is a mixture of experts model, which is
significantly larger, taking roughly ~100GB disk space (TODO: concrete number)
and performs better than `Mistral7B`.


* `Mistral7B` + `fp16` (cuda). 24+GB perferred. needs 48GB GPU to run all the demos (some of them have a context as long as ~10k).
* `Mistral7B` + `8bit` (cuda). at least 12+GB. 24+GB preferred (so you can run all demo).
* `Mistral7B` + `4bit` (cuda). at least 6+GB. 12+GB preferred (so you can run all demo).
* `Mistral7B` + `fp32` (cpu). This requires 64+GB of RAM, but CPU is at least 100~400 times slower than GPU on this. Not recommended.

* `Mixtral8x7B` + `fp16`. 90+GB
* `Mixtral8x7B` + `8bit`. 45+GB
* `Mixtral8x7B` + `4bit`. 23+GB. But in order to run all the demo, you still need 2x 48GB GPUs in 4bit precision, as the context length is ~10k.

Note, Multi-GPU inference is supported.
If you have multiple GPUs, this memory requirement for each GPU is roughly divided by your number of GPUs.
See also https://huggingface.co/blog/mixtral

# Usage of `debgpt` (main user interface)

```shell
debgpt                  # you need to do "pip3 install ." first.
debgpt -F openai        # use the openai frontend
debgpt -h               # print supported taskss, and the the arguments shared across all tasks
debgpt <task> -h        # print the help of a task
```

check `demo.sh` at the root directory for a list of samples.
The configuration file is located at `~/.debgpt/config.toml`.
Check `/etc/config.toml` for example.


# Usage (developers)

The (debugging) tag means the corresponding usage is for debugging purpose.
The (backend) tag means the corresponding usage is for self-hosted LLM inference. You only need a backend if the ZMQ frontend is used.

## `llm.py` LLM inference (debugging)

Directly calling this module is to chat with an LLM locally.

```
python3 -m debgpt.llm
```

## `backend.py` exposes llm inference through ZMQ (backend

The following command starts the backend server, specifying the max length of LLM response.
By default the program will automatically use the CUDA device if it is available on the system.
If not, you can still run the model on CPU. But note that "fp16" (half float precision) is not
supported for CPU. Each reasponse may takes a couple of minutes on CPU, or a couple of seconds on GPU.
Here I provided multiple preicisions. You can always trade-off the precision for some speed and RAM/CUDA memory requirement.
The argument `max_new_tokens` does not matter much and you can adjust it (it is the maximum length of each llm reply).

```
# (default: cuda) assume you have a 24+GB CUDA device
# the GPU can reply within seconds
debgpt backend --max_new_tokens=1024 --device cuda

# (cuda) assume you have a 12+GB CUDA device
debgpt backend --max_new_tokens=1024 --device cuda --precision 8bit

# (cuda) assume you have a 6+GB CUDA device (something like RTX 4070Ti will do)
debgpt backend --max_new_tokens=1024 --device cuda --precision 4bit

# (cpu) if you want to use CPU. make sure you have 64+GB system RAM.
# This is really slow. It takes roughly 20 minutes for Xeon Gold 6140 to calculate one reply in the pytorch debian/rules example in demo.sh
# the other precisions are not supported. 8bit/4bit quantization needs GPU. fp16/bf16 not implemented on cpu. only fp32 available here.
debgpt backend --max_new_tokens=1024 --device cpu --precision fp32
```

If you want to run the Mixtral8x7B model (much larger) instead of the default Mistral7B:

```
# check the above hardware requirement first.
debgpt backend --llm Mixtral8x7B --max_new_tokens=1024 --device cuda --precision 4bit
```

## `frontend.py` collection of frontends, like ZMQ and OpenAI (debugging)

The main user interface will wrap the frontend.

```shell
$ python3 -m debgpt.frontend
```
