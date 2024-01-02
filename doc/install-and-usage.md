# Setup

The default step requires a nvidia driver that supports at least CUDA 11.8

### Conda / Mamba

1. Install [miniconda distribution](https://docs.conda.io/projects/miniconda/en/latest/miniconda-other-installer-links.html).
For instance, `bash Miniconda3-py310_23.11.0-2-Linux-x86_64.sh -b -p ~/miniconda3`.
1. `conda init <your-default-shell>` and source the config again.
For instance, if you use bash: `~/miniconda3/bin/conda init bash; source ~/.bashrc`;
if you use fish: `~/miniconda3/bin/conda init fish; source ~/.config/fish/config.fish`
2. (Optional) install mamba from conda-forge to replace conda.
`conda install -c conda-forge mamba` ; `mamba init <shell>` (e.g., `mamba init fish`); `source <shell-rc>`.
We do this because the default conda is super slow and may sometimes fail to resolve dependencies.
If this step is skipped, replace the `mamba` into `conda` for all the following commands.
3. `mamba env create -f conda.yml`. To restore the conda environment.
4. `mamba activate pth212`. Then we are good.

### Venv + Pip

1. `python3 -m venv ~/.debgpt/venv`
2. `source ~/.debgpt/venv/bin/activate.fish` change to your default shell.
3. `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118` (from https://pytorch.org)
4. `pip3 install transformers accelerate bitsandbytes bitsandbytes`
5. `pip3 install beautifulsoup4 rich prompt_toolkit ipython`
6. `pip3 install pyzmq pytest`
7. we are good now.


# Install (optional)

Just `pip3 install .` for `pyproject.toml`-based project.
If this step is skipped, just replace `debgpt` into `python3 -m debgpt.main_cli` in every command that starts with `debgpt`.

# Usage

* `llm.py` LLM inference engine abstraction. 
Directly calling this module is to chat with an LLM locally.

```
python3 -m debgpt.llm
```

* `backend.py` exposes LLM instance through ZMQ.
The following command starts the backend server, specifying the max length of LLM response.
By default the program will automatically use the CUDA device if it is available on the system.
If not, you can still run the model on CPU. But note that "fp16" (half float precision) is not
supported for CPU. Each reasponse may takes a couple of minutes on CPU, or a couple of seconds on GPU.
Here I provided multiple preicisions. You can always trade-off the precision for some speed and RAM/CUDA memory requirement.

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

* `frontend.py` is a bare ZMQ client. This command is mainly used for debugging.
The main user interface will wrap the frontend.

```shell
$ python3 -m debgpt.frontend
```

* `main_cli.py` main user interface. The following two commands are equilvalent

```shell
python3 -m debgpt.main_cli    # development mode
debgpt                        # you need to do "pip3 install ." first.
```
