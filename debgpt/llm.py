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


class vLLM_Mistral7BInstruct(AbstractLLM):
    __model_id__ = 'mistralai/Mistral-7B-Instruct-v0.2'
    def __init__(self):
        super().__init__()
        raise NotImplementedError
        # TODO: https://github.com/vllm-project/vllm


class Mistral7BInstruct(AbstractLLM):
    '''
    https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    '''
    __model_id__ = 'mistralai/Mistral-7B-Instruct-v0.2'

    def __init__(self, precision: str = 'fp16'):
        super().__init__()
        console.log(f'Mistral7BInstruct> Loading {self.__model_id__} ({precision})')
        llm_args = {'torch_dtype': {'fp32': th.float32, 'fp16': th.float16}[precision],
                    'load_in_4bit': True if precision == '4bit' else False}
        self.model = AutoModelForCausalLM.from_pretrained(self.__model_id__, **llm_args).to(0)
        self.tokenizer = AutoTokenizer.from_pretrained(self.__model_id__)
        self.model.to(self.device)

    def example(self):
        messages = [
                {"role": "user", "content": "What is your favourite condiment?"},
                {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"},
                {"role": "user", "content": "Do you have mayonnaise recipes?"}
                ]
        decoded = self.generate(messages)
        console.print(decoded)

    @th.no_grad() 
    def generate(self, messages):
        encoded = self.tokenizer.apply_chat_template(messages, return_tensors='pt').to(0)
        model_inputs = encoded.to(self.device)
        generated_ids = self.model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
        decoded = self.tokenizer.batch_decode(generated_ids)
        return decoded

    def simple(self, user_input: str, *, max_new_tokens: int=100):
        encoded = self.tokenizer(user_input, return_tensors='pt').to(0)
        return self.model.generate(**encoded, max_new_tokens=max_new_tokens)

    def interactive(self):
        while message := prompt('User>'):
            response = self.simple(message)
            decoded = self.tokenizer.batch_decode(response)
            console.print('LLM>', decoded[0])


if __name__ == '__main__':
    llm = Mistral7BInstruct()
    import IPython
    IPython.embed(color='neutral')
