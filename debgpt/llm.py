# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import rich
console = rich.get_console()
import torch as th
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
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
    https://docs.mistral.ai/models/
    https://huggingface.co/docs/transformers/model_doc/mistral
    https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    '''
    model_id = 'mistralai/Mistral-7B-Instruct-v0.2'

    def __init__(self):
        '''
        dtype: float32 requires 32GB CUDA memory.
               bfloat16 (default) requires CUDA compute > 8.0 due to vLLM itself.
               float16 has better compatibility than bfloat16 through vllm.
        '''
        super().__init__()
        console.log(f'Mistral7B> Loading {self.model_id} (float16)')
        self.llm = AutoModelForCausalLM.from_pretrained(self.model_id,
                                                        torch_dtype=th.float16)
        self.llm.to(self.device)
        self.tok = AutoTokenizer.from_pretrained(self.model_id)
        self.kwargs = {'max_new_tokens': 128, 'do_sample': True,
                       'pad_token_id': 2}

    @th.no_grad() 
    def generate(self, text: Union[list,str]):
        if isinstance(text, list):
            encoded = self.tok.apply_chat_template(text, return_tensors='pt').to(0)
            model_inputs = encoded.to(self.device)
            generated_ids = self.llm.generate(model_inputs, **self.kwargs)
            decoded = self.tok.batch_decode(generated_ids)
        elif isinstance(text, str):
            encoded = self.tok([text], return_tensors='pt').to(0)
            model_inputs = encoded.to(self.device)
            generated_ids = self.llm.generate(**model_inputs, **self.kwargs)
        else:
            raise TypeError(f'text type {type(text)} is not supprted')
        decoded = self.tok.batch_decode(generated_ids)
        return decoded

    def interactive(self):
        while text := prompt('Prompt> '):
            response = self.generate(text)
            console.print('LLM> ', response[0])

    def example(self):
        decoded = self.generate('who are you?')
        console.print(decoded)
        messages = [
                {"role": "user", "content": "What is your favourite condiment?"},
                {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"},
                {"role": "user", "content": "Do you have mayonnaise recipes?"}
                ]
        decoded = self.generate(messages)
        console.print(decoded)


if __name__ == '__main__':
    llm = Mistral7B()
    import IPython
    IPython.embed(colors'neutral')
