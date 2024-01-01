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
import os
import json


class AbstractLLM(object):
    def __init__(self):
        self.device='cuda' if th.cuda.is_available() else 'cpu'
    @th.no_grad()
    def generate(self, messages: Union[list,str]):
        # Used by backend.py for serving a client
        raise NotImplementedError
    @th.no_grad()
    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)
    def chat(self):
        # chat with LLM locally
        raise NotImplementedError
    def interact(self):
        # XXX: ipython here is for debugging
        import IPython
        IPython.embed(colors='neutral')


class Mistral7B(AbstractLLM):
    '''
    https://docs.mistral.ai/models/
    https://huggingface.co/docs/transformers/model_doc/mistral
    https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    https://huggingface.co/docs/transformers/main/chat_templating

    TODO: also support 4bit and 8bit for CPU inference. Not everybody has expensive GPUs.
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
        self.kwargs = {'max_new_tokens': 512,
                       'do_sample': True,
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
            # not recommended to use in this way. This is used for debugging
            # You may need to manually format the prompt into [INST] user input text [/INST] to make LLM work properly.
            encoded = self.tok([messages], return_tensors='pt').to(0)
            model_inputs = encoded.to(self.device)
            generated_ids = self.llm.generate(**model_inputs, **self.kwargs)
        else:
            raise TypeError(f'messages type {type(messages)} is not supprted')
        decoded = self.tok.batch_decode(generated_ids)
        return messages, decoded


    def chat(self, chat = Conversation()):
        '''
        https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.ConversationalPipeline
        '''
        pipe = pipeline('conversational', model=self.llm, tokenizer=self.tok, device=self.device)
        try:
            while text := prompt('Prompt> '):
                chat.add_message({'role': 'user', 'content': text})
                chat = pipe(chat, **self.kwargs)
                console.print('LLM> ', chat[-1]['content'])
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
        return chat


def create_llm(args) -> AbstractLLM:
    # factory
    if ag.llm == 'Mistral7B':
        model = Mistral7B()
        model.kwargs['max_new_tokens'] = args.max_new_tokens
    else:
        raise NotImplementedError(f'{args.llm} is not yet implemented')
    return model


if __name__ == '__main__':
    ag = argparse.ArgumentParser('Chat with LLM locally.')
    ag.add_argument('--max_new_tokens', type=int, default=512, help='max length of new token sequences added by llm')
    ag.add_argument('--debgpt_home', type=str, default=os.path.expanduser('~/.debgpt'))
    ag.add_argument('--llm', type=str, default='Mistral7B', choices=('Mistral7B',))
    ag = ag.parse_args()
    console.log(ag)

    if not os.path.exists(ag.debgpt_home):
        os.mkdir(ag.debgpt_home)

    # load model and start chat
    llm = create_llm(ag)
    log = llm.chat()

    # save a record
    fpath = os.path.join(ag.debgpt_home, str(log.uuid) + '.json')
    with open(fpath, 'wt') as f:
        json.dump(log.messages, f)

    console.log(f'LLM chat session saved at {fpath}')
