"""
This is the file that contains any instances or functions, classes that can be used globally.
"""

import base64
import os
import os.path
import tempfile
import threading
import time
import wave
from pathlib import Path

import anthropic
import google.generativeai as genai
import pyaudio
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMessageBox
from openai import OpenAI

from pyqt_openai import STT_MODEL, OPENAI_ENDPOINT_DICT, PLATFORM_MODEL_DICT, DEFAULT_GEMINI_MODEL, LLAMA_REQUEST_URL, \
    OPENAI_CHAT_ENDPOINT
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamapage_script import GPTLLamaIndexWrapper

os.environ['OPENAI_API_KEY'] = ''

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = GPTLLamaIndexWrapper()

OPENAI_CLIENT = OpenAI(api_key='')
GEMINI_CLIENT = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
CLAUDE_CLIENT = anthropic.Anthropic(api_key='')
LLAMA_CLIENT = OpenAI(
    api_key='',
    base_url=LLAMA_REQUEST_URL
)

OPENAI_API_VALID = False

def set_openai_enabled(f):
    global OPENAI_API_VALID
    OPENAI_API_VALID = f
    return OPENAI_API_VALID

def is_openai_enabled():
    return OPENAI_API_VALID

def set_openai_api_key(api_key):
    os.environ['OPENAI_API_KEY'] = api_key
    OPENAI_CLIENT.api_key = os.environ['OPENAI_API_KEY']

def set_api_key(env_var_name, api_key):
    if env_var_name == 'GEMINI_API_KEY':
        genai.configure(api_key=api_key)
    if env_var_name == 'CLAUDE_API_KEY':
        CLAUDE_CLIENT.api_key = api_key
    if env_var_name == 'LLAMA_API_KEY':
        LLAMA_CLIENT.api_key = api_key

def get_model_endpoint(model):
    for k, v in OPENAI_ENDPOINT_DICT.items():
        endpoint_group = list(v)
        if model in endpoint_group:
            return k

def get_openai_chat_model():
    return OPENAI_ENDPOINT_DICT[OPENAI_CHAT_ENDPOINT]

def get_chat_model():
    all_models = [model for models in PLATFORM_MODEL_DICT.values() for model in models]
    return all_models

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

def get_gpt_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
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

# Check which platform a specific model belongs to
def get_platform_from_model(model):
    for platform, models in PLATFORM_MODEL_DICT.items():
        if model in models:
            return platform
    return None

def get_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                 use_max_tokens, max_tokens,
                 images,
                 is_llama_available=False, is_json_response_available=0,
                 json_content=None
                 ):
    try:
        platform = get_platform_from_model(model)
        if platform == 'OpenAI':
            args = get_gpt_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                     use_max_tokens, max_tokens,
                     images,
                     is_llama_available=is_llama_available, is_json_response_available=is_json_response_available,
                     json_content=json_content
                     )
        elif platform == 'Gemini':
            args = {
                'model': model,
                'messages': messages,
                'stream': stream
            }
            args['messages'].append({"role": "user", "content": cur_text})
        elif platform == 'Claude':
            args = {
                'model': model,
                'messages': messages,
                'max_tokens': 1024,
                'stream': stream
            }
            args['messages'].append({"role": "user", "content": cur_text})
        elif platform == 'Llama':
            args = {
                'model': model,
                'messages': messages,
                'stream': stream,
                'max_tokens': 1024
            }
            args['messages'].append({"role": "user", "content": cur_text})
        else:
            raise Exception(f'Platform not found for model {model}')
        return args
    except Exception as e:
        print(e)
        raise e

def get_response(args, get_content_only=True):
    platform = get_platform_from_model(args['model'])
    if platform == 'OpenAI':
        response = OPENAI_CLIENT.chat.completions.create(
            **args
        )
        if args['stream']:
            for chunk in response:
                response_text = chunk.choices[0].delta.content
                yield response_text
        else:
            if get_content_only:
                return response.choices[0].message.content
            else:
                return response
    elif platform == 'Gemini':
        # Change 'content' to 'parts'
        # Change role's value from 'assistant' to 'model'
        for message in args['messages']:
            message['parts'] = message.pop('content')
            if message['role'] == 'assistant':
                message['role'] = 'model'

        chat = GEMINI_CLIENT.start_chat(
            history=args['messages']
        )

        if args['stream']:
            response = chat.send_message(args['messages'][-1]['parts'], stream=args['stream'])
            for chunk in response:
                yield chunk.text
        else:
            response = chat.send_message(args['messages'][-1]['parts'])
            if get_content_only:
                return response.text
            else:
                return response
    elif platform == 'Claude':
        if args['stream']:
            with CLAUDE_CLIENT.messages.stream(
                    model=args['model'],
                    max_tokens=1024,
                    messages=args['messages']
            ) as stream:
                for text in stream.text_stream:
                    yield text
        else:
            response = CLAUDE_CLIENT.messages.create(
                model=args['model'],
                max_tokens=1024,
                messages=args['messages']
            )
            if get_content_only:
                return response.content[0].text
            else:
                return response
    elif platform == 'Llama':
        response = LLAMA_CLIENT.chat.completions.create(
            **args
        )
        if args['stream']:
            for chunk in response:
                response_text = chunk.choices[0].delta.content
                yield response_text
        else:
            if get_content_only:
                return response.choices[0].message.content
            else:
                return response

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

# TTS
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

            with OPENAI_CLIENT.audio.speech.with_streaming_response.create(
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

# STT
def check_microphone_access():
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        stream.close()
        audio.terminate()
        return True
    except Exception as e:
        return False

class RecorderThread(QThread):
    recording_finished = Signal(str)
    errorGenerated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__stop = False

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            chunk = 1024  # Record in chunks of 1024 samples
            sample_format = pyaudio.paInt16  # 16 bits per sample
            channels = 2
            fs = 44100  # Record at 44100 samples per second

            p = pyaudio.PyAudio()  # Create an interface to PortAudio

            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=fs,
                            frames_per_buffer=chunk,
                            input=True)

            frames = []  # Initialize array to store frames

            # Store data in chunks for the specified time
            while True:
                if self.__stop:
                    break
                data = stream.read(chunk)
                frames.append(data)

            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                filename = tmpfile.name

            # Save the recorded data as a WAV file in the temporary file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))
            wf.close()

            self.recording_finished.emit(filename)
        except Exception as e:
            if str(e).find('-9996') != -1:
                self.errorGenerated.emit(LangClass.TRANSLATIONS[
                                             'No valid input device found. Please connect a microphone or check your audio device settings.'])
            else:
                self.errorGenerated.emit(f'<p style="color:red">{e}</p>')


class STTThread(QThread):
    stt_finished = Signal(str)
    errorGenerated = Signal(str)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        try:
            transcript = OPENAI_CLIENT.audio.transcriptions.create(
                model=STT_MODEL,
                file=Path(self.filename)
            )
            self.stt_finished.emit(transcript.text)
        except Exception as e:
            self.errorGenerated.emit(f'<p style="color:red">{e}</p>')
        finally:
            os.remove(self.filename)


class ChatThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: streaming or not streaming
    Third: ChatMessageContainer
    """
    replyGenerated = Signal(str, bool, ChatMessageContainer)
    streamFinished = Signal(ChatMessageContainer)

    def __init__(self, input_args, info: ChatMessageContainer):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        self.__info = info
        self.__info.role = 'assistant'

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            if self.__input_args['stream']:
                response = get_response(self.__input_args)
                for chunk in response:
                    if self.__stop:
                        self.__info.finish_reason = 'stopped by user'
                        self.streamFinished.emit(self.__info)
                        break
                    else:
                        self.replyGenerated.emit(chunk, True, self.__info)
                self.__info.finish_reason = 'stop'
                self.streamFinished.emit(self.__info)
            else:
                response = get_response(self.__input_args)

                self.__info.content = response
                # TODO tokenizer
                self.__info.prompt_tokens = ''
                self.__info.completion_tokens = ''
                self.__info.total_tokens = ''
                self.__info.finish_reason = 'stop'
                self.replyGenerated.emit(response, False, self.__info)
        except Exception as e:
            self.__info.finish_reason = 'Error'
            self.__info.content = f'<p style="color:red">{e}</p>'
            self.replyGenerated.emit(self.__info.content, False, self.__info)