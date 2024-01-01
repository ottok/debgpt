# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import rich
console = rich.get_console()
import torch as th
import numpy as np
import vllm
from prompt_toolkit import prompt


class AbstractLLM(object):
    def __init__(self):
        self.device='cuda' if th.cuda.is_available() else 'cpu'
    def generate(self, model_inputs):
        raise NotImplementedError
    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)


class Mistral7B(AbstractLLM):
    '''
    https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    https://github.com/vllm-project/vllm
    '''
    __model_id__ = 'mistralai/Mistral-7B-Instruct-v0.2'
    __impl__ = 'vllm'

    def __init__(self, *, dtype: str='float16'):
        '''
        dtype: float32 requires 32GB CUDA memory.
               bfloat16 (default) requires CUDA compute > 8.0 due to vLLM itself.
               float16 has better compatibility than bfloat16 through vllm.
        '''
        super().__init__()
        console.log(f'Mistral7B> Loading {self.__model_id__} ({dtype})')
        self.llm = vllm.LLM(model='mistralai/Mistral-7B-Instruct-v0.2', dtype=dtype)
        self.sampling_params = vllm.SamplingParams(temperature=0.8, top_p=0.95)

    def generate(self, prompt: Union[List,str]):
        prompt = [prompt] if isinstance(prompt, str) else prompt
        outputs = self.llm.generate(prompt, self.sampling_params)
        return [(output.prompt, output.outputs[0].text) for output in outputs]

    def interactive(self):
        while message := prompt('Prompt>'):
            response = self.generate(message)
            console.print('LLM>', response[0][1])

if __name__ == '__main__':
    llm = Mistral7B()
    import IPython
    IPython.embed(color='neutral')
