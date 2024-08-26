"""
This is the file that contains the database and llama-index instance, OpenAI API related constants.
Also this checks the version of the OpenAI package and raises an exception if the version is below 1.0.
"""

import base64
import os.path

from openai import OpenAI

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamapage_script import GPTLLamaIndexWrapper

os.environ['OPENAI_API_KEY'] = ''

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = GPTLLamaIndexWrapper()

# initialize
OPENAI_STRUCT = OpenAI(api_key='')

OPENAI_API_VALID = False

def setOpenAIEnabled(f):
    global OPENAI_API_VALID
    OPENAI_API_VALID = f
    return OPENAI_API_VALID

def isOpenAIEnabled():
    return OPENAI_API_VALID

def setApiKeyAndClientGlobal(api_key):
    # for subprocess (mostly)
    os.environ['OPENAI_API_KEY'] = api_key
    OPENAI_STRUCT.api_key = os.environ['OPENAI_API_KEY']


# https://platform.openai.com/docs/models/model-endpoint-compatibility
ENDPOINT_DICT = {
    '/v1/chat/completions': ['gpt-4o', 'gpt-4o-mini'],
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

def get_image_url_from_local(image):
    """
    Image is bytes, this function converts it to base64 and returns the image url
    """
    # Function to encode the image
    def encode_image(image):
        return base64.b64encode(image).decode('utf-8')

    base64_image = encode_image(image)
    return f'data:image/jpeg;base64,{base64_image}'

def get_message_obj(role, content):
    return {"role": role, "content": content}

def get_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                     use_max_tokens, max_tokens,
                     images,
                     is_llama_available=False, is_json_response_available=0,
                     json_content=None
                 ):
    try:
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
        if is_json_response_available:
            openai_arg['response_format'] = {"type": 'json_object'}
            cur_text += f' JSON {json_content}'

        # If there is at least one image, it should add
        if len(images) > 0:
            multiple_images_content = []
            for image in images:
                multiple_images_content.append(
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': get_image_url_from_local(image),
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
    except Exception as e:
        print(e)
        raise e

def form_response(response, info: ChatMessageContainer):
    info.content = response.choices[0].message.content
    info.prompt_tokens = response.usage.prompt_tokens
    info.completion_tokens = response.usage.completion_tokens
    info.total_tokens = response.usage.total_tokens
    info.finish_reason = response.choices[0].finish_reason
    return info


def init_llama():
    llama_index_directory = CONFIG_MANAGER.get_general_property('llama_index_directory')
    if llama_index_directory and CONFIG_MANAGER.get_general_property(
            'use_llama_index'):
        LLAMAINDEX_WRAPPER.set_directory(llama_index_directory)