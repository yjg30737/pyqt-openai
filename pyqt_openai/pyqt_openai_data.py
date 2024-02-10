import base64
import json

import openai
import requests
from openai.types.chat import ChatCompletion

from pyqt_openai.sqlite import SqliteDatabase

DB = SqliteDatabase()

# if openai version is below 1.0, this will be empty and not being used
OPENAI_STRUCT = ''
if openai.__version__ >= str(1.0):
    from openai import OpenAI

    # initialize
    OPENAI_STRUCT = OpenAI(api_key='')

# https://platform.openai.com/docs/models/model-endpoint-compatibility
ENDPOINT_DICT = {
    '/v1/chat/completions': ['gpt-4-0125-preview', 'gpt-4', 'gpt-4-1106-preview', 'gpt-4-vision-preview',
                             'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'],
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

def get_argument(model, system, previous_text, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                 use_max_tokens, max_tokens,
                 images,
                 is_llama_available):
    # Form argument
    openai_arg = {
        'model': model,
        'messages': [
            {"role": "system", "content": system},
            {"role": "assistant", "content": previous_text},
        ],
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

    # If current model is "gpt-4-1106-preview", default max token set to very low number by openai,
    # so let's set this to 4096 which is relatively better.
    if is_gpt_vision(model):
        openai_arg['max_tokens'] = 4096

    if is_llama_available:
        del openai_arg['messages']
    if use_max_tokens:
        openai_arg['max_tokens'] = max_tokens

    return openai_arg

def form_response(response, info_dict):
    if isinstance(response, ChatCompletion):
        response_text = response.choices[0].message.content
        info_dict['prompt_tokens'] = response.usage.prompt_tokens
        info_dict['completion_tokens'] = response.usage.completion_tokens
        info_dict['total_tokens'] = response.usage.total_tokens
        info_dict['finish_reason'] = response.choices[0].finish_reason
    else:
        response_text = response['choices'][0]['message']['content']
        info_dict['prompt_tokens'] = response['usage']['prompt_tokens']
        info_dict['completion_tokens'] = response['usage']['completion_tokens']
        info_dict['total_tokens'] = response['usage']['total_tokens']
        info_dict['finish_reason'] = response['choices'][0]['finish_reason']
    return response_text, info_dict

def get_vision_response(openai_arg, info_dict):
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {OPENAI_STRUCT.api_key}"
    }

    # TODO
    # Support stream
    # Before that, i will temporarily set stream as false
    openai_arg['stream'] = False
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=openai_arg)
    response = json.loads(response.text)
    response_text, info_dict = form_response(response, info_dict)
    return response_text, info_dict

    # with requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=openai_arg,
    #                    stream=True) as resp:
    #     # try/except way to handle JSONDecodeError is not recommended, so i will change soon
    #     try:
    #         for line in resp.iter_lines():
    #             if line:
    #                 yield json.loads(':'.join(line.decode('utf8').split(':')[1:]).strip())
    #     except JSONDecodeError as e:
    #         pass

def is_gpt_vision(model: str):
    return model == 'gpt-4-vision-preview'
