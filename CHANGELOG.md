Changelog
=========

v0.4.92 -- 2024-01-08
---------------------

Major changes:

* Use `debgpt genconfig` to auto-generate the config.toml template.
The original manually written one at `etc/config.toml` was deprecated.

* Implemented ordered argparse. The complicated argument order such
as `-f file1.txt --man man -f file2` will be correctly reflected in
the generated prompt.

Minor changes:

* Reorganize code and do the chore. Make CLI less verbose. More pytests.

v0.4.91 -- 2024-01-07
---------------------

Major bug fix:

* 87fb088 bring batch the accidentally deleted function

Minor updates:

* 3cc2d26 Add function to parse the order of selected arguments in the command line interface. (wip)
* 3a3eca4 make: add make install starget

v0.4.90 -- 2024-01-07
---------------------

Development release with massive breaking and major changes.

Breaking changes:

* Redesign CLI. It is more flexible and easier to use now. Please refer the
examples in README or the manpage. It is too long to describe here.

Major changes:

* Merge all doc in README.md and rewrite a portion of them.
* Make README.md compatible to manpage through pandoc.
* Overall all documentations and reorganize them.
* Support more text loaders for CLI.
* Rewrite argument subparsers for the CLI.

Minor changes:

* Merged all examples from demo.sh to README.md
* Remove conda environment YAML files. No longer necessary.
* Split pytest code to dedicated tests directory.
* Strip pytest from dependencies.
* Miscellaneous code organization.
* Removed replay examples in examples/ directory.
* Add debianization fiiles.

This release note is not written by LLM.

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

