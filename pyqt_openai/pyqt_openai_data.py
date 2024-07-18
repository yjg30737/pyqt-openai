import base64
import json
import os.path

import openai
import requests
from openai.types.chat import ChatCompletion

from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamapage_script import GPTLLamaIndexWrapper

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = GPTLLamaIndexWrapper()

# if openai version is below 1.0, exit the program and suggest to upgrade
if openai.__version__ < str(1.0):
    raise Exception('Please upgrade openai package to version 1.0 or higher')

from openai import OpenAI

# initialize
OPENAI_STRUCT = OpenAI(api_key='')

ROOT_DIR = os.path.dirname(__file__)

# https://platform.openai.com/docs/models/model-endpoint-compatibility
ENDPOINT_DICT = {
    '/v1/chat/completions': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo',
                             'gpt-3.5-turbo'],
    '/v1/completions': [
        'text-davinci-003', 'text-davinci-002', 'text-curie-001', 'text-babbage-001', 'text-ada-001', 'davinci',
        'curie', 'babbage', 'ada'
    ],
    '/v1/edits': ['text-davinci-edit-001', 'code-davinci-edit-001'],
    '/v1/audio/transcriptions': ['whisper-1'],
    '/v1/audio/translations': ['whisper-1'],
    '/v1/fine-tunes': ['davinci', 'curie', 'babbage', 'ada'],
    '/v1/embeddings': ['text-embedding-ada-002', 'text-search-ada-doc-001'],
    '/vi/moderations': ['text-moderation-stable', 'text-moderation-latest']
}

# This doesn't need endpoint
DALLE_ARR = ['dall-e-2', 'dall-e-3']

def get_model_endpoint(model):
    for k, v in ENDPOINT_DICT.items():
        endpoint_group = list(v)
        if model in endpoint_group:
            return k

def get_chat_model():
    return ENDPOINT_DICT['/v1/chat/completions']

def get_image_url_from_local(image_path):
    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
          return base64.b64encode(image_file.read()).decode('utf-8')

    base64_image = encode_image(image_path)
    return f'data:image/jpeg;base64,{base64_image}'

def get_message_obj(role, content):
    return {"role": role, "content": content}

def get_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                 use_max_tokens, max_tokens,
                 images,
                 is_llama_available=False):
    system_obj = get_message_obj("system", system)
    messages = [system_obj] + messages

    # Form argument
    openai_arg = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'top_p': top_p,
        'frequency_penalty': frequency_penalty,
        'presence_penalty': presence_penalty,
        'stream': stream,
    }
    # If there is at least one image, it should add
    if len(images) > 0:
        multiple_images_content = []
        for image in images:
            multiple_images_content.append(
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': get_image_url_from_local(image)
                    }
                }
            )

        multiple_images_content = [
                                      {
                                          "type": "text",
                                          "text": cur_text
                                      }
                                  ] + multiple_images_content[:]
        openai_arg['messages'].append({"role": "user", "content": multiple_images_content})
    else:
        openai_arg['messages'].append({"role": "user", "content": cur_text})

    if is_llama_available:
        del openai_arg['messages']
    if use_max_tokens:
        openai_arg['max_tokens'] = max_tokens

    return openai_arg

def form_response(response, info: ChatMessageContainer):
    info.content = response.choices[0].message.content
    info.prompt_tokens = response.usage.prompt_tokens
    info.completion_tokens = response.usage.completion_tokens
    info.total_tokens = response.usage.total_tokens
    info.finish_reason = response.choices[0].finish_reason
    return info