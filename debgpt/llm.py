'''
MIT License

Copyright (c) 2024 Mo Zhou <lumin@debian.org>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import json
import os
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from transformers import pipeline, Conversation
from transformers import AutoModelForCausalLM, AutoTokenizer
import transformers
from transformers import TextStreamer
import torch as th
from typing import Union, List, Dict
import argparse
import rich
console = rich.get_console()


class AbstractLLM(object):
    def __init__(self):
        self.device = 'cuda' if th.cuda.is_available() else 'cpu'

    @th.no_grad()
    def generate(self, messages: Union[list, str]):
        # Used by backend.py for serving a client
        raise NotImplementedError

    @th.no_grad()
    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)

    def chat(self):
        # chat with LLM locally
        raise NotImplementedError


class Mistral7B(AbstractLLM):
    '''
    https://docs.mistral.ai/models/
    https://huggingface.co/docs/transformers/model_doc/mistral
    https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    https://huggingface.co/docs/transformers/main/chat_templating
    https://huggingface.co/blog/mixtral
    '''
    NAME = 'Mistral7B'
    model_id = 'mistralai/Mistral-7B-Instruct-v0.2'
    is_pipeline = True

    def __init__(self, *, device: str, precision: str):
        '''
        torch_dtype: th.float32 requires 32GB CUDA memory.
                     th.float16/th.bfloat16 requires 16GB CUDA memory.
                     th.float16 has better hardware compatibility than bfloat16.
                     th.float16 has better compatibility than bfloat16.
        '''
        super().__init__()
        self.device = device  # override abstract class
        console.log(
            f'{self.NAME}> Loading {self.model_id} ({device}/{precision})')
        self.tok = AutoTokenizer.from_pretrained(self.model_id)
        llm_kwargs = {'torch_dtype': th.float16,
                      'load_in_8bit': False, 'load_in_4bit': False}
        if precision == 'fp16':
            llm_kwargs['torch_dtype'] = th.float16
        elif precision == 'fp32':
            llm_kwargs['torch_dtype'] = th.float32
        elif precision == 'bf16':
            llm_kwargs['torch_dtype'] = th.bfloat16
        elif precision == '8bit':
            llm_kwargs['load_in_8bit'] = True
        elif precision == '4bit':
            llm_kwargs['load_in_4bit'] = True
            llm_kwargs['bnb_4bit_compute_dtype'] = th.float16
        else:
            raise NotImplementedError(precision)
        if self.is_pipeline:
            self.llm = transformers.pipeline('text-generation', model=self.model_id,
                                             model_kwargs=llm_kwargs, tokenizer=self.tok, device_map='auto' if self.device == 'cuda' else self.device)
        else:
            self.llm = AutoModelForCausalLM.from_pretrained(
                self.model_id, llm_kwargs)
        if precision in ('fp16', 'fp32', 'bf16') and not self.is_pipeline:
            self.llm.to(self.device)
        else:
            pass
        self.kwargs = {'max_new_tokens': 512,
                       'do_sample': True,
                       'pad_token_id': 2,
                       # default parameters for mixtral
                       # https://huggingface.co/blog/mixtral
                       'temperature': 0.7,
                       'top_k': 50,
                       'top_p': 0.95,
                       }

    @th.no_grad()
    def generate(self, messages: List[Dict]):
        if self.is_pipeline:
            templated = self.tok.apply_chat_template(messages, tokenize=False,
                                                     add_generation_prompt=True)
            outputs = self.llm(templated, **self.kwargs)
            generated = outputs[0]['generated_text'][len(templated):].lstrip()
            messages.append({'role': 'assistant', 'content': generated})
            return messages
        else:
            encoded = self.tok.apply_chat_template(messages, tokenize=True,
                                                   return_tensors='pt',
                                                   add_generation_prompt=True).to(0)
            model_inputs = encoded.to(self.device)
            input_length = model_inputs.shape[1]
            generated_ids = self.llm.generate(model_inputs, **self.kwargs)
            generated_new_ids = generated_ids[:, input_length:]
            generated_new_text = self.tok.batch_decode(generated_new_ids,
                                                       skip_special_tokens=True,
                                                       clean_up_tokenization_spaces=True)[0]
            new_message = {'role': 'assistant', 'content': generated_new_text}
            messages.append(new_message)
            return messages

    def chat(self, chat=Conversation()):
        '''
        https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.ConversationalPipeline
        '''
        if self.is_pipeline:
            pipe = self.llm
        else:
            pipe = pipeline('conversational', model=self.llm,
                            tokenizer=self.tok, device=self.device)

        streamer = TextStreamer(
            self.tok, skip_prompt=True, clean_up_tokenization_spaces=True, skip_special_tokens=True)
        prompt_style = Style(
            [('prompt', 'bold fg:ansibrightcyan'), ('', 'ansiwhite')])
        try:
            while text := prompt(f'Prompt[{len(chat.messages)}]> ', style=prompt_style):
                chat.add_message({'role': 'user', 'content': text})
                if True:
                    if self.is_pipeline:
                        templated = self.tok.apply_chat_template(chat.messages, tokenize=False,
                                                                 add_generation_prompt=True)
                        print(
                            f'\x1b[1;32mStream[{len(chat.messages)}]>\x1b[0m \x1b[0;32m', end='')
                        outputs = pipe(
                            templated, **self.kwargs, streamer=streamer, clean_up_tokenization_spaces=True)
                        print('\x1b[0m', end='')
                        generated = outputs[0]['generated_text'][len(
                            templated):]
                        chat.add_message(
                            {'role': 'assistant', 'content': generated})
                    else:
                        chat = pipe(chat, **self.kwargs)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
        return chat


class Mixtral8x7B(Mistral7B):
    NAME = 'Mixtral8x7B'
    model_id = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
    is_pipeline = True


def create_llm(args) -> AbstractLLM:
    # factory
    if args.llm == 'Mistral7B':
        model = Mistral7B(device=args.device, precision=args.precision)
        model.kwargs['max_new_tokens'] = args.max_new_tokens
    elif args.llm == 'Mixtral8x7B':
        model = Mixtral8x7B(device=args.device, precision=args.precision)
        model.kwargs['max_new_tokens'] = args.max_new_tokens
    else:
        raise NotImplementedError(f'{args.llm} is not yet implemented')
    return model


if __name__ == '__main__':
    ag = argparse.ArgumentParser('Chat with LLM locally.')
    ag.add_argument('--max_new_tokens', type=int, default=512,
                    help='max length of new token sequences added by llm')
    ag.add_argument('--debgpt_home', type=str,
                    default=os.path.expanduser('~/.debgpt'))
    ag.add_argument('--llm', type=str, default='Mistral7B',
                    choices=('Mistral7B', 'Mixtral8x7B'))
    ag.add_argument('-i', '--ipython', action='store_true')
    ag.add_argument('--device', type=str,
                    default='cuda' if th.cuda.is_available() else 'cpu')
    ag.add_argument('--precision', type=str,
                    default='fp16' if th.cuda.is_available() else '4bit')
    ag = ag.parse_args()
    console.log(ag)

    if not os.path.exists(ag.debgpt_home):
        os.mkdir(ag.debgpt_home)

    # for debugging
    if ag.ipython:
        llm = create_llm(ag)
        # XXX: ipython here is for debugging
        msg = [{'role': 'user', 'content': 'hi!'}]
        import IPython
        IPython.embed(colors='neutral')
        exit()

    # load model and start chat
    llm = create_llm(ag)
    log = llm.chat()

    # save a record
    fpath = os.path.join(ag.debgpt_home, str(log.uuid) + '.json')
    with open(fpath, 'wt') as f:
        json.dump(log.messages, f)

    console.log(f'LLM chat session saved at {fpath}')
