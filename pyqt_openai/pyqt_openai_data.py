"""
This is the file that contains the database and llama-index instance, OpenAI API related constants.
"""

import base64
import io
import os.path
import time
import threading

import pyaudio
from PySide6.QtWidgets import QMessageBox
from openai import OpenAI

from pyqt_openai import STT_MODEL
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamapage_script import GPTLLamaIndexWrapper

os.environ['OPENAI_API_KEY'] = ''

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = GPTLLamaIndexWrapper()

OPENAI_STRUCT = OpenAI(api_key='')

OPENAI_API_VALID = False


def set_openai_enabled(f):
    global OPENAI_API_VALID
    OPENAI_API_VALID = f
    return OPENAI_API_VALID

def is_openai_enabled():
    return OPENAI_API_VALID

def set_api_key_and_client_global(api_key):
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

class StreamThread(threading.Thread):
    def __init__(self, input_args, stop_callback):
        super().__init__()
        self.input_args = input_args
        self.stop_event = threading.Event()
        self.stop_callback = stop_callback
        self.daemon = True

    def run(self):
        try:
            player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

            start_time = time.time()

            with OPENAI_STRUCT.audio.speech.with_streaming_response.create(
                    **self.input_args,
                    response_format="pcm",  # similar to WAV, but without a header chunk at the start.
            ) as response:
                print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
                for chunk in response.iter_bytes(chunk_size=1024):
                    if self.stop_event.is_set():
                        print("Stream interrupted.")
                        break
                    player_stream.write(chunk)

                print(f"Done in {int((time.time() - start_time) * 1000)}ms.")

        finally:
            if self.stop_callback:
                self.stop_callback()

    def stop(self):
        self.stop_event.set()

def stream_to_speakers(input_args, stop_callback=None):
    stream_thread = StreamThread(input_args, stop_callback)
    stream_thread.start()
    return stream_thread


def check_microphone_access():
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        stream.close()
        audio.terminate()
        return True
    except Exception as e:
        return False


def record(FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=44100, CHUNK=1024, RECORD_SECONDS=5, WAVE_OUTPUT_FILENAME="output.wav"):
    audio = pyaudio.PyAudio()

    MIC_RECORDING = True

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording start...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        if MIC_RECORDING:
            data = stream.read(CHUNK)
            frames.append(data)
        else:
            break

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    buffer = io.BytesIO()
    # you need to set the name with the extension
    buffer.name = 'tmp.mp3'
    audio.export(buffer, format="mp3")

    transcript = OPENAI_STRUCT.audio.transcriptions.create(
        model=STT_MODEL,
        file=b''.join(frames)
    )
    print(transcript.text)

    # Save as WAV file


def start_recording():
    if not check_microphone_access():
        QMessageBox.information(None, 'Microphone Access', 'Microphone access is not granted')
        return False
    else:
        print('Recording started...')
        record()
        return True


def stop_recording():
    print('Recording stopped...')