Changelog
=========

v0.4.0 -- 2024-01-04
--------------------

Breaking changes:

* the `-i (--iteractive)` command line option is removed. Interactive mode is the default now.
* `replay.py` is moved inside `debgpt/`. Use `debgpt replay` instead.

Majore changes:

* Refactor the subparsers in `main_cli.py`. The cmdline behavior slightly
  changed. For instance, previously `debgpt` will tell you what task it
  supports, but now it will directly enter the interaction with LLM without
  auto-generated first prompt. It is equivant to `debgpt none`. Use `debgpt
  -h/--help` to lookup tasks instead. Use `debgpt <task> -h` to check arguments
  for each task.
* Implemented the `dryrun` frontend. It quits after generating the first
  prompt. You can copy and paste this prompt into free-of-charge web-based
  LLMs.

Changes:

- Updated `demo.sh` script to use `debgpt replay` instead of `python3 replay.py`.
- Moved the `replay` functionality inside the `debgpt` directory.
- Added `-M` shortcut option for `--openai_model_id`.
- Added `--hide_first_prompt` option to improve user experience for certain tasks.
- Updated the documentation.
- Added `--multiline` support for prompt toolkit.
- Implemented a dry-run frontend to generate prompts for free web-based LLM.
- Suppressed all warnings in the CLI.
- Added support for `--temperature` and `--top_p` arguments.
- Improved documentation by adding links and updating example config.

v0.3.0 -- 2024-01-03
--------------------

Major updates:

* support OpenAI API now. you can specify `--openai_model_id` to specify a model.
When OpenAI Frontend is used, we will enable the streaming mode, which prints
LLM outputs in real time (word by word) to the terminal.

Minor updates:

* optimize frontend/cli loading speed.
* support config file (default is ~/.debgpt/config.toml)
* added `debgpt stdin < some-file.txt` and `debgpt file ... none`.
* fix device for pipeline when the user specified cpu.

v0.2.1 -- 2024-01-03
--------------------

This is a minor feature update.

* llm: switch to streaming mode when chatting locally. The LLM will
  generate tokens one by one in real-time.

v0.2 -- 2024-01-02
------------------

This is a Feature release

* llm: add Mixtral8x7B model.
* llm: switch to transformers.pipeline to enable multi-gpu inference

v0.1 -- 2024-01-02
-------------------

This is the Initial release.
