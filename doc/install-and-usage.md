# Setup

The default step requires a GPU that supports CUDA compatibility 7.0 or higher (e.g., V100, RTX20XX, A100, etc)

### Conda / Mamba

1. Install [miniconda distribution](https://docs.conda.io/projects/miniconda/en/latest/miniconda-other-installer-links.html).
For instance, `bash Miniconda3-py310_23.11.0-2-Linux-x86_64.sh -b -p ~/miniconda3`.
1. `conda init <your-default-shell>` and source the config again.
For instance, if you use bash: `~/miniconda3/bin/conda init bash; source ~/.bashrc`;
if you use fish: `~/miniconda3/bin/conda init fish; source ~/.config/fish/config.fish`
2. (Optional) install mamba from conda-forge to replace conda.
`conda install -c conda-forge mamba` ; `mamba init <shell>`; `source <shell-rc>`.
We do this because the default conda is super slow and may sometimes fail to resolve dependencies.
If this step is skipped, replace the `mamba` into `conda` for all the following commands.
3. `mamba env create -f conda.yml`. To restore the conda environment.
4. `mamba activate pth212`. Then we are good.

### Venv + Pip

TODO

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

```
python3 -m debgpt.backend --max_new_tokens=1024
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
