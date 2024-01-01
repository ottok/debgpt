# Copyright (C) 2024 Mo Zhou <lumin@debian.org>
# MIT/Expat License.
from typing import *
import argparse
import rich
from rich.panel import Panel
console = rich.get_console()
import torch as th
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline, Conversation
from prompt_toolkit import prompt
import re


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
    https://huggingface.co/docs/transformers/main/chat_templating
    '''
    model_id = 'mistralai/Mistral-7B-Instruct-v0.2'

    def __init__(self, *, torch_dtype=th.float16):
        '''
        torch_dtype: th.float32 requires 32GB CUDA memory.
                     th.float16/th.bfloat16 requires 16GB CUDA memory.
                     th.float16 has better hardware compatibility than bfloat16.
                     th.float16 has better compatibility than bfloat16.
        '''
        super().__init__()
        console.log(f'Mistral7B> Loading {self.model_id} (float16)')
        self.llm = AutoModelForCausalLM.from_pretrained(self.model_id,
                                                        torch_dtype=torch_dtype)
        self.llm.to(self.device)
        self.tok = AutoTokenizer.from_pretrained(self.model_id)
        self.kwargs = {'max_new_tokens': 512, 'do_sample': True,
                       'pad_token_id': 2}

    @th.no_grad() 
    def generate(self, messages: Union[list,str]):
        if isinstance(messages, list):
            encoded = self.tok.apply_chat_template(messages, tokenize=True,
                                                   return_tensors='pt',
                                                   add_generatio_prompt=True).to(0)
            model_inputs = encoded.to(self.device)
            generated_ids = self.llm.generate(model_inputs, **self.kwargs)
        elif isinstance(messages, str):
            encoded = self.tok([messages], return_tensors='pt').to(0)
            model_inputs = encoded.to(self.device)
            generated_ids = self.llm.generate(**model_inputs, **self.kwargs)
        else:
            raise TypeError(f'messages type {type(messages)} is not supprted')
        decoded = self.tok.batch_decode(generated_ids)
        return decoded


    def chat(self):
        '''
        https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.ConversationalPipeline
        '''
        pipe = pipeline('conversational', model=self.llm, tokenizer=self.tok, device=self.device)
        chat = Conversation()
        try:
            while text := prompt('Prompt> '):
                chat.add_message({'role': 'user', 'content': text})
                chat = pipe(chat)
                console.print('LLM> ', chat[-1]['content'])
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass


    def interact(self):
        '''
        Interact while keeping the history.
        '''
        tokenized_chat = []
        try:
            while text := prompt('Prompt> '):
                tokenized_chat.append({'role': 'user', 'content': text})
                response = self.generate(tokenized_chat)[0]
                console.print(Panel(response, title='DEBUG'), markup=False)

                dedup = self.tok.apply_chat_template(tokenized_chat, tokenize=False)
                response = response.lstrip(dedup)

                response = re.sub(r'^.*\[/INST\]', '', response) # It should be greedy.
                response = re.sub(r'</s>', '', response)
                response = response.strip()
                console.print('LLM> ', response, markup=False)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass

    def example(self):
        messages = [
                {"role": "user", "content": "What is your favourite condiment?"},
                {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"},
                {"role": "user", "content": "Do you have mayonnaise recipes?"}
                ]
        decoded = self.generate(messages)
        console.print(decoded)
        return decoded


if __name__ == '__main__':
    llm = Mistral7B()
    import IPython
    IPython.embed(colors='neutral')
