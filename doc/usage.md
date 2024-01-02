# Usage

## `llm.py` LLM inference engine abstraction.

This module allows you to directly chat with an LLM locally.

```
python3 -m debgpt.llm
```

## `backend.py` exposes an LLM instance through ZMQ

```
python3 -m debgpt.backend --max_new_tokens=1024     # start the server
```

## `frontend.py` is a bare ZMQ client which communicates with the backend instance

```shell
$ python3 -m debgpt.frontend          # mainly used for debugging
```

## `main_cli.py` is the main user interface.

The following two commands are equilvalent

```shell
python3 -m debgpt.main_cli    # development mode
debgpt                        # you need to do "pip3 install ." first.
```
