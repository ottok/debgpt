Changelog
=========

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
