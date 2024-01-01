
## Setup / Install

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

### Apt + Venv + Pip

TODO

