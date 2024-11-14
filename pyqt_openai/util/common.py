"""
This file includes utility functions that are used in various parts of the application.
Mostly, these functions are used to perform chat-related tasks such as sending and receiving messages
or common tasks such as opening a directory, generating random strings, etc.
Some of the functions are used to set PyQt settings, restart the application, show message boxes, etc.
"""

import asyncio
import base64
import json
import os
import random
import re
import string
import subprocess
import sys
import tempfile
import time
import traceback
import wave
import zipfile

from datetime import datetime
from io import BytesIO
from pathlib import Path

import PIL.Image
import numpy as np
import psutil
from g4f import ProviderType
from g4f.providers.base_provider import ProviderModelMixin
from litellm import completion

from pyqt_openai.widgets.scrollableErrorDialog import ScrollableErrorDialog

if sys.platform == "win32":
    import winreg

import pyaudio

from PySide6.QtCore import Qt, QUrl, QThread, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QFrame
from g4f.Provider import ProviderUtils, __providers__, __map__
from g4f.errors import ProviderNotFoundError
from g4f.models import ModelUtils
from g4f.providers.retry_provider import IterProvider
from jinja2 import Template

import pyqt_openai.util
from pyqt_openai import (
    MAIN_INDEX,
    PROMPT_MAIN_KEY_NAME,
    PROMPT_BEGINNING_KEY_NAME,
    PROMPT_END_KEY_NAME,
    PROMPT_JSON_KEY_NAME,
    CONTEXT_DELIMITER,
    THREAD_ORDERBY,
    DEFAULT_APP_NAME,
    AUTOSTART_REGISTRY_KEY,
    is_frozen,
    G4F_PROVIDER_DEFAULT,
    PROVIDER_MODEL_DICT,
    O1_MODELS,
    OPENAI_ENDPOINT_DICT,
    OPENAI_CHAT_ENDPOINT,
    STT_MODEL,
    DEFAULT_DATETIME_FORMAT,
    DEFAULT_TOKEN_CHUNK_SIZE,
)
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.globals import (
    DB,
    OPENAI_CLIENT,
    G4F_CLIENT,
    LLAMAINDEX_WRAPPER,
    REPLICATE_CLIENT,
)
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer, ChatMessageContainer


def get_generic_ext_out_of_qt_ext(text):
    pattern = r"\((\*\.(.+))\)"
    match = re.search(pattern, text)
    extension = "." + match.group(2) if match.group(2) else ""
    return extension


def open_directory(path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def message_list_to_txt(db, thread_id, title, username="User", ai_name="AI"):
    content = ""
    certain_thread_filename_content = db.selectCertainThreadMessagesRaw(thread_id)
    content += f"== {title} ==" + CONTEXT_DELIMITER
    for unit in certain_thread_filename_content:
        unit_prefix = username if unit[2] == 1 else ai_name
        unit_content = unit[3]
        content += f"{unit_prefix}: {unit_content}" + CONTEXT_DELIMITER
    return content


def is_valid_regex(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def conv_unit_to_html(db, id, title):
    certain_conv_filename_content = db.selectCertainThreadMessagesRaw(id)
    chat_history = [unit[3] for unit in certain_conv_filename_content]
    template = Template(
        """
    <html>
        <head>
            <title>pyqt-openai html file - {{ title }}</title>
            <style>
                .chat {
                    background-color: #f2f2f2;
                    border-radius: 5px;
                    padding: 10px;
                }
                .message {
                    padding: 2rem;
                }
                .message:nth-child(even) {
                    background-color: #ddd; /* Color for even messages */
                }
                
                .message:nth-child(odd) {
                    background-color: #fff; /* Color for odd messages */
                }
            </style>
        </head>
        <body>
            <header>
                <h1>{{ title }}</h1>
            </header>
            <div class="chat">
                {% for message in chat_history %}
                    <div class="message">{{ message }}</div>
                {% endfor %}
            </div>
        </body>
    </html>
    """
    )
    html = template.render(title=title, chat_history=chat_history)
    return html


def add_file_to_zip(file_content, file_name, output_zip_file):
    with zipfile.ZipFile(output_zip_file, "a") as zipf:
        zipf.writestr(file_name, file_content)


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def get_image_filename_for_saving(arg: ImagePromptContainer):
    ext = ".png"
    filename_prompt_prefix = "_".join(
        "".join(re.findall("[a-zA-Z0-9\\s]", arg.prompt[:20])).split(" ")
    )
    size = f"{arg.width}x{arg.height}"
    filename = (
        "_".join(map(str, [filename_prompt_prefix, size]))
        + "_"
        + generate_random_string(8)
        + ext
    )

    return filename


def get_image_prompt_filename_for_saving(directory, filename):
    txt_filename = os.path.join(directory, Path(filename).stem + ".txt")
    return txt_filename


def restart_app():
    # Define the arguments to be passed to the executable
    args = [sys.executable, MAIN_INDEX]
    # Call os.execv() to execute the new process
    os.execv(sys.executable, args)


def show_message_box_after_change_to_restart(change_list):
    title = LangClass.TRANSLATIONS["Application Restart Required"]
    text = LangClass.TRANSLATIONS[
        "The program needs to be restarted because of following changes"
    ]
    text += "\n\n" + "\n".join(change_list) + "\n\n"
    text += LangClass.TRANSLATIONS["Would you like to restart it?"]

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
    result = msg_box.exec()
    return result


def get_chatgpt_data_for_preview(filename, most_recent_n: int = None):
    data = json.load(open(filename, "r"))
    conv_arr = []
    for i in range(len(data)):
        conv = data[i]
        conv_dict = {}
        name = conv["title"]
        insert_dt = (
            datetime.fromtimestamp(conv["create_time"]).strftime(
                DEFAULT_DATETIME_FORMAT
            )
            if conv["create_time"]
            else None
        )
        update_dt = (
            datetime.fromtimestamp(conv["update_time"]).strftime(
                DEFAULT_DATETIME_FORMAT
            )
            if conv["update_time"]
            else None
        )
        conv_dict["id"] = conv["id"]
        conv_dict["name"] = name
        conv_dict["insert_dt"] = insert_dt
        conv_dict["update_dt"] = update_dt
        conv_dict["mapping"] = conv["mapping"]
        conv_arr.append(conv_dict)

    conv_arr = sorted(conv_arr, key=lambda x: x[THREAD_ORDERBY], reverse=True)
    if most_recent_n is not None:
        conv_arr = conv_arr[:most_recent_n]

    return {"columns": ["id", "name", "insert_dt", "update_dt"], "data": conv_arr}


def get_chatgpt_data_for_import(conv_arr):
    for conv in conv_arr:
        conv["messages"] = []
        for k, v in conv["mapping"].items():
            obj = {}
            message = v["message"]
            if message:
                metadata = message["metadata"]

                role = message["author"]["role"]
                create_time = (
                    datetime.fromtimestamp(message["create_time"]).strftime(
                        DEFAULT_DATETIME_FORMAT
                    )
                    if message["create_time"]
                    else None
                )
                update_time = (
                    datetime.fromtimestamp(message["update_time"]).strftime(
                        DEFAULT_DATETIME_FORMAT
                    )
                    if message["update_time"]
                    else None
                )
                content = message["content"]

                obj["role"] = role
                obj["insert_dt"] = create_time
                obj["update_dt"] = update_time

                if role == "user":
                    content_parts = "\n".join([str(c) for c in content["parts"]])
                    obj["content"] = content_parts
                    conv["messages"].append(obj)
                else:
                    if role == "tool":
                        pass
                    elif role == "assistant":
                        model_slug = metadata.get("model_slug", None)
                        obj["model"] = model_slug
                        content_type = content["content_type"]
                        # Text (General chat)
                        if content_type == "text":
                            content_parts = "\n".join(content["parts"])
                            obj["content"] = content_parts
                            conv["messages"].append(obj)
                        elif content_type == "code":
                            # Currently there is no way to apply every aspect of the "code" content_type into the code.
                            # So let it be for now.
                            pass
                    elif role == "system":
                        # Won't use the system
                        pass
    # Remove mapping keys
    for conv in conv_arr:
        del conv["mapping"]

    return conv_arr


def is_prompt_group_name_valid(text):
    """
    Check if the prompt group name is valid or not and exists in the database
    :param text: The text to check
    """
    text = text.strip()
    if not text:
        return False
    # Check if the prompt group with same name already exists
    if DB.selectCertainPromptGroup(name=text):
        return False
    return True


def is_prompt_entry_name_valid(group_id, text):
    """
    Check if the prompt entry name is valid or not and exists in the database
    :param group_id: The group id to check
    :param text: The text to check
    """
    text = text.strip()
    # Check if the prompt entry with same name already exists
    exists_f = (
        True
        if (True if text else False)
        and DB.selectPromptEntry(group_id=group_id, name=text)
        else False
    )
    return exists_f


def validate_prompt_group_json(json_data):
    # Check if json_data is a list
    if not isinstance(json_data, list):
        return False

    # Iterate through each item in the list
    for item in json_data:
        # Check if item is a dictionary
        if not isinstance(item, dict):
            return False

        # Check if 'name' and 'data' keys exist in the dictionary
        if "name" not in item or "data" not in item:
            return False

        # Check if 'name' is not empty
        if not item["name"]:
            return False

        # Check if 'data' is a list
        if not isinstance(item["data"], list):
            return False

        # Iterate through each data item in 'data' list
        for data_item in item["data"]:
            # Check if data_item is a dictionary
            if not isinstance(data_item, dict):
                return False

            # Check if 'name' and 'content' keys exist in data_item
            if "name" not in data_item or "content" not in data_item:
                return False

            # Check if 'name' in data_item is not empty
            if not data_item["name"]:
                return False

    return True


def get_prompt_data(prompt_type="form"):
    data = []
    for group in DB.selectPromptGroup(prompt_type=prompt_type):
        group_obj = {"name": group.name, "data": []}
        for entry in DB.selectPromptEntry(group.id):
            group_obj["data"].append({"name": entry.name, "content": entry.content})
        data.append(group_obj)
    return data


def showJsonSample(json_sample_widget, json_sample):
    json_sample_widget.setText(json_sample)
    json_sample_widget.setReadOnly(True)
    json_sample_widget.setMinimumSize(600, 350)
    json_sample_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    json_sample_widget.setWindowTitle(LangClass.TRANSLATIONS["JSON Sample"])
    json_sample_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    json_sample_widget.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.WindowCloseButtonHint
        | Qt.WindowType.WindowStaysOnTopHint
    )
    json_sample_widget.show()


def get_content_of_text_file_for_send(filenames: list[str]):
    """
    Get the content of the text file for sending to the AI
    :param filenames: The list of filenames to get the content from
    :return: The content of the text file
    """
    source_context = ""
    for filename in filenames:
        base_filename = os.path.basename(filename)
        source_context += f"=== {base_filename} start ==="
        source_context += CONTEXT_DELIMITER
        with open(filename, "r", encoding="utf-8") as f:
            source_context += f.read()
        source_context += CONTEXT_DELIMITER
        source_context += f"=== {base_filename} end ==="
        source_context += CONTEXT_DELIMITER
    prompt_context = f"== Source Start ==\n{source_context}== Source End =="
    return prompt_context


# FIXME This should be used but this has a couple of flaws that need to be fixed
def moveCursorToOtherPrompt(direction, textGroup):
    """
    Move the cursor to another prompt based on the direction
    :param direction: The direction to move the cursor to
    :param textGroup: The prompt in the group to move the cursor to
    """

    def switch_focus(from_key, to_key):
        """Switch focus from one text edit to another if both are visible."""
        if textGroup[from_key].isVisible() and textGroup[from_key].hasFocus():
            if textGroup[to_key].isVisible():
                textGroup[from_key].clearFocus()
                textGroup[to_key].setFocus()

    if direction == "up":
        switch_focus(PROMPT_MAIN_KEY_NAME, PROMPT_BEGINNING_KEY_NAME)
        switch_focus(PROMPT_END_KEY_NAME, PROMPT_JSON_KEY_NAME)
        switch_focus(PROMPT_END_KEY_NAME, PROMPT_MAIN_KEY_NAME)
        switch_focus(PROMPT_JSON_KEY_NAME, PROMPT_MAIN_KEY_NAME)
    elif direction == "down":
        switch_focus(PROMPT_BEGINNING_KEY_NAME, PROMPT_MAIN_KEY_NAME)
        switch_focus(PROMPT_MAIN_KEY_NAME, PROMPT_JSON_KEY_NAME)
        switch_focus(PROMPT_MAIN_KEY_NAME, PROMPT_END_KEY_NAME)
        switch_focus(PROMPT_JSON_KEY_NAME, PROMPT_END_KEY_NAME)
    else:
        print("Invalid direction:", direction)


def getSeparator(orientation="horizontal"):
    sep = QFrame()
    if orientation == "horizontal":
        sep.setFrameShape(QFrame.Shape.HLine)
    elif orientation == "vertical":
        sep.setFrameShape(QFrame.Shape.VLine)
    else:
        raise ValueError("Invalid orientation")
    sep.setFrameShadow(QFrame.Shadow.Sunken)
    return sep


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler.
    This should be only used in release mode.
    """
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Unhandled exception: {error_msg}")

    msg_box = ScrollableErrorDialog(error_msg)
    msg_box.exec()


def set_auto_start_windows(enable: bool):
    # If OS is not Windows, return
    if sys.platform != "win32":
        return

    # If this is not a frozen application, return
    if not is_frozen():
        return

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, AUTOSTART_REGISTRY_KEY, 0, winreg.KEY_WRITE
    )

    if enable:
        exe_path = sys.executable  # Current executable path
        winreg.SetValueEx(key, DEFAULT_APP_NAME, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, DEFAULT_APP_NAME)
        except FileNotFoundError:
            pass


def generate_random_prompt(arr):
    if len(arr) > 0:
        max_len = max(map(lambda x: len(x), arr))
        weights = [i for i in range(max_len, 0, -1)]
        random_prompt = ", ".join(
            list(
                filter(
                    lambda x: x != "",
                    [random.choices(_, weights[: len(_)])[0] for _ in arr],
                )
            )
        )
    else:
        random_prompt = ""
    return random_prompt


def get_g4f_models():
    models = list(ModelUtils.convert.keys())
    return models


def convert_to_provider(provider: str):
    if " " in provider:
        provider_list = [
            ProviderUtils.convert[p]
            for p in provider.split()
            if p in ProviderUtils.convert
        ]
        if not provider_list:
            raise ProviderNotFoundError(f"Providers not found: {provider}")
        provider = IterProvider(provider_list)
    elif provider in ProviderUtils.convert:
        provider = ProviderUtils.convert[provider]
    elif provider:
        raise ProviderNotFoundError(f"Provider not found: {provider}")
    return provider


def get_g4f_providers(including_auto=False):
    providers = list(
        provider.__name__ for provider in __providers__ if provider.working
    )
    if including_auto:
        providers = [G4F_PROVIDER_DEFAULT] + providers
    return providers


def get_g4f_models_by_provider(provider):
    provider = ProviderUtils.convert[provider]
    models = []
    if hasattr(provider, "models"):
        models = provider.models if provider.models else []
    return models


def get_g4f_providers_by_model(model, including_auto=False):
    providers = get_g4f_providers()
    supported_providers = []

    for provider in providers:
        provider = ProviderUtils.convert[provider]

        if hasattr(provider, "models"):
            models = provider.models if provider.models else models
            if model in models:
                supported_providers.append(provider)

    supported_providers = [
        provider.get_dict()["name"] for provider in supported_providers
    ]

    if including_auto:
        supported_providers = [G4F_PROVIDER_DEFAULT] + supported_providers

    return supported_providers


def get_chat_model(is_g4f=False):
    if is_g4f:
        return get_g4f_models()
    else:
        all_models = [
            model for models in PROVIDER_MODEL_DICT.values() for model in models
        ]
        return all_models

def get_gemini_argument(model, system, messages, cur_text, stream, images):
    try:
        args = {
            "system": system,
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if len(images) > 0:
            args["images"] = [PIL.Image.open(BytesIO(image)) for image in images]
        args["messages"].append({"role": "user", "content": cur_text})
        return args
    except Exception as e:
        print(e)
        raise e


def get_claude_argument(model, system, messages, cur_text, stream, images):
    try:
        args = {
            "model": model,
            "system": system,
            "messages": messages,
            "max_tokens": DEFAULT_TOKEN_CHUNK_SIZE,
            "stream": stream,
        }
        # TODO REFACTORING (FOR COMMON FUNCTION FOR VISION)
        # Vision
        if len(images) > 0:
            multiple_images_content = []
            for image in images:
                multiple_images_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": get_image_url_from_local(image),
                        },
                    }
                )

            multiple_images_content = multiple_images_content[:] + [
                {"type": "text", "text": cur_text}
            ]

            args["messages"].append(
                {"role": "user", "content": multiple_images_content}
            )
        else:
            args["messages"].append({"role": "user", "content": cur_text})
        return args
    except Exception as e:
        print(e)
        raise e


def set_api_key(env_var_name, api_key):
    api_key = api_key.strip() if api_key else ""
    if env_var_name == "OPENAI_API_KEY":
        OPENAI_CLIENT.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    if env_var_name == "GEMINI_API_KEY":
        os.environ["GEMINI_API_KEY"] = api_key
    if env_var_name == "CLAUDE_API_KEY":
        os.environ["ANTHROPIC_API_KEY"] = api_key
    if env_var_name == "REPLICATE_API_KEY":
        REPLICATE_CLIENT.api_key = api_key
        os.environ["REPLICATE_API_KEY"] = api_key
        os.environ["REPLICATE_API_TOKEN"] = api_key

    # Set environment variables dynamically
    os.environ[env_var_name] = api_key


def get_openai_model_endpoint(model):
    for k, v in OPENAI_ENDPOINT_DICT.items():
        endpoint_group = list(v)
        if model in endpoint_group:
            return k


def get_openai_chat_model():
    return OPENAI_ENDPOINT_DICT[OPENAI_CHAT_ENDPOINT]


def get_image_url_from_local(image, is_openai=False):
    """
    Image is bytes, this function converts it to base64 and returns the image url
    """

    # Function to encode the image
    def encode_image(image):
        return base64.b64encode(image).decode("utf-8")

    base64_image = encode_image(image)
    if is_openai:
        return f"data:image/jpeg;base64,{base64_image}"
    else:
        return base64_image


def get_message_obj(role, content):
    return {"role": role, "content": content}


# Check which provider a specific model belongs to
def get_provider_from_model(model):
    for provider, models in PROVIDER_MODEL_DICT.items():
        if model in models:
            return provider
    return None


def get_g4f_image_models() -> list:
    """
    Get all the models that support image generation
    Some of the image providers are not included in this list
    """
    image_models = []
    index = []
    for provider in __providers__:
        if hasattr(provider, "image_models"):
            if hasattr(provider, "get_models"):
                provider.get_models()
            parent = provider
            if hasattr(provider, "parent"):
                parent = __map__[provider.parent]
            if parent.__name__ not in index:
                for model in provider.image_models:
                    image_models.append(
                        {
                            "provider": parent.__name__,
                            "url": parent.url,
                            "label": parent.label if hasattr(parent, "label") else None,
                            "image_model": model,
                        }
                    )
                    index.append(parent.__name__)

    models = [model["image_model"] for model in image_models]
    return models


def get_g4f_image_providers(including_auto=False) -> list:
    """
    Get all the providers that support image generation
    (Even though this is not a perfect way to get the providers that support image generation)
    (So i have to bring get_providers function directly from g4f library)
    """

    def get_providers():
        """
        The function get from g4f/gui/server/api.py
        """
        return {
            provider.__name__: (
                provider.label if hasattr(provider, "label") else provider.__name__
            )
            + (" (WebDriver)" if "webdriver" in provider.get_parameters() else "")
            + (" (Auth)" if provider.needs_auth else "")
            for provider in __providers__
            if provider.working
        }

    providers = get_providers()
    if including_auto:
        providers = [G4F_PROVIDER_DEFAULT] + [provider for provider in providers]
    return providers


def get_g4f_image_models_from_provider(provider) -> list:
    """
    Get all the models that support image generation for a specific provider
    (Again, this is not a perfect way to get the models that support image generation)
    (So i have to bring get_provider_models function directly from g4f library)
    """
    if provider == G4F_PROVIDER_DEFAULT:
        return get_g4f_image_models()

    def get_provider_models(provider: str) -> list[dict]:
        """
        From g4f/gui/server/api.py
        """
        if provider in __map__:
            provider: ProviderType = __map__[provider]
            if issubclass(provider, ProviderModelMixin):
                return [
                    {"model": model, "default": model == provider.default_model}
                    for model in provider.get_models()
                ]
            elif provider.supports_gpt_35_turbo or provider.supports_gpt_4:
                return [
                    *(
                        [{"model": "gpt-4", "default": not provider.supports_gpt_4}]
                        if provider.supports_gpt_4
                        else []
                    ),
                    *(
                        [
                            {
                                "model": "gpt-3.5-turbo",
                                "default": not provider.supports_gpt_4,
                            }
                        ]
                        if provider.supports_gpt_35_turbo
                        else []
                    ),
                ]
            else:
                return []

    return [model["model"] for model in get_provider_models(provider)]


def get_g4f_argument(model, messages, cur_text, stream, images):
    args = {"model": model, "messages": messages, "stream": stream, "images": images}
    args["messages"].append({"role": "user", "content": cur_text})
    return args


def get_api_argument(
    model,
    system,
    messages,
    cur_text,
    temperature,
    top_p,
    frequency_penalty,
    presence_penalty,
    stream,
    use_max_tokens,
    max_tokens,
    images,
    is_llama_available=False,
    is_json_response_available=0,
    json_content=None,
):
    try:
        if model in O1_MODELS:
            stream = False
        else:
            system_obj = get_message_obj("system", system)
            messages = [system_obj] + messages

        # Form argument
        arg = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": stream,
        }
        if is_json_response_available:
            arg["response_format"] = {"type": "json_object"}
            cur_text += f" JSON {json_content}"

        # If there is at least one image, it should add
        if len(images) > 0:
            multiple_images_content = []
            for image in images:
                multiple_images_content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": get_image_url_from_local(image, is_openai=True),
                        },
                    }
                )

            multiple_images_content = [
                {"type": "text", "text": cur_text}
            ] + multiple_images_content[:]
            arg["messages"].append(
                {"role": "user", "content": multiple_images_content}
            )
        else:
            arg["messages"].append({"role": "user", "content": cur_text})

        if is_llama_available:
            del arg["messages"]
        if use_max_tokens:
            arg["max_tokens"] = max_tokens

        return arg
    except Exception as e:
        print(e)
        raise e


def get_argument(
    model,
    system,
    messages,
    cur_text,
    temperature,
    top_p,
    frequency_penalty,
    presence_penalty,
    stream,
    use_max_tokens,
    max_tokens,
    images,
    is_llama_available=False,
    is_json_response_available=0,
    json_content=None,
    is_g4f=False,
):
    try:
        if is_g4f:
            args = get_g4f_argument(model, messages, cur_text, stream, images)
        else:
            args = get_api_argument(
                model,
                system,
                messages,
                cur_text,
                temperature,
                top_p,
                frequency_penalty,
                presence_penalty,
                stream,
                use_max_tokens,
                max_tokens,
                images,
                is_llama_available=is_llama_available,
                is_json_response_available=is_json_response_available,
                json_content=json_content,
            )
        return args
    except Exception as e:
        print(e)
        raise e


def stream_response(response, is_g4f=False, get_content_only=True):
    if is_g4f:
        if get_content_only:
            for chunk in response:
                yield chunk.choices[0].delta.content
        else:
            for chunk in response:
                yield chunk
    else:
        for part in response:
            yield part.choices[0].delta.content or ""


def get_api_response(args, get_content_only=True):
    try:
        response = completion(drop_params=True, **args)
        if args["stream"]:
            return stream_response(response)
        else:
            return response.choices[0].message.content or ""
    except Exception as e:
        print(e)
        raise e


def get_g4f_response(args, get_content_only=True):
    try:
        response = G4F_CLIENT.chat.completions.create(**args)
        if args["stream"]:
            return stream_response(
                response=response,
                is_g4f=True,
                get_content_only=get_content_only,
            )
        else:
            if get_content_only:
                return response.choices[0].message.content
            else:
                return response
    except Exception as e:
        print(e)
        raise e


def get_response(args, is_g4f=False, get_content_only=True, provider=""):
    """
    Get the response from the API
    :param args: The arguments to pass to the API
    :param is_g4f: Whether the model is G4F or not
    :param get_content_only: Whether to get the content only or not
    :param provider: The provider of the model (Auto if not provided)
    """
    try:
        if is_g4f:
            if provider != G4F_PROVIDER_DEFAULT:
                args["provider"] = convert_to_provider(provider)
            return get_g4f_response(args, get_content_only=False)
        else:
            return get_api_response(args, get_content_only)
    except Exception as e:
        print(e)
        raise e


# This has to be here because of the circular import problem
def init_llama():
    llama_index_directory = CONFIG_MANAGER.get_general_property("llama_index_directory")
    if llama_index_directory and CONFIG_MANAGER.get_general_property("use_llama_index"):
        LLAMAINDEX_WRAPPER.set_directory(llama_index_directory)


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


# TTS
class TTSThread(QThread):
    errorGenerated = Signal(str)

    def __init__(self, voice_provider, input_args):
        super().__init__()
        self.voice_provider = voice_provider
        self.input_args = input_args
        self.__stop = False

    def run(self):
        try:
            if self.voice_provider == "OpenAI":
                player_stream = pyaudio.PyAudio().open(
                    format=pyaudio.paInt16, channels=1, rate=24000, output=True
                )
                with OPENAI_CLIENT.audio.speech.with_streaming_response.create(
                    **self.input_args,
                    response_format="pcm",  # similar to WAV, but without a header chunk at the start.
                ) as response:
                    for chunk in response.iter_bytes(
                        chunk_size=DEFAULT_TOKEN_CHUNK_SIZE
                    ):
                        if self.__stop:
                            break
                        player_stream.write(chunk)
            elif self.voice_provider == "edge-tts":
                media = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                media.close()
                mp3_fname = media.name

                subtitle = tempfile.NamedTemporaryFile(suffix=".vtt", delete=False)
                subtitle.close()
                vtt_fname = subtitle.name

                print(f"Media file: {mp3_fname}")
                print(f"Subtitle file: {vtt_fname}\n")

                if sys.platform == "win32":
                    with subprocess.Popen(
                        [
                            "edge-tts",
                            f"--write-media={mp3_fname}",
                            f"--write-subtitles={vtt_fname}",
                            f"--voice={self.input_args['voice']}",
                            f"--text={self.input_args['input']}",
                        ],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    ) as process:
                        process.communicate()
                else:
                    with subprocess.Popen(
                        [
                            "edge-tts",
                            f"--write-media={mp3_fname}",
                            f"--write-subtitles={vtt_fname}",
                            f"--voice={self.input_args['voice']}",
                            f"--text={self.input_args['input']}",
                        ],
                    ) as process:
                        process.communicate()

                proc = subprocess.Popen(
                    [
                        "mpv",
                        f"--sub-file={vtt_fname}",
                        mp3_fname,
                    ],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                while proc.poll() is None:
                    time.sleep(0.1)
                    if self.__stop:
                        kill(proc.pid)
                        break
                if mp3_fname is not None and os.path.exists(mp3_fname):
                    os.unlink(mp3_fname)
                if vtt_fname is not None and os.path.exists(vtt_fname):
                    os.unlink(vtt_fname)
        except Exception as e:
            error_text = f'<p style="color:red">{e}</p>'

            # TODO LANGUAGE
            if self.voice_provider == "OpenAI":
                error_text += "<br>(Are you registered valid OpenAI API Key? This feature requires OpenAI API Key.)"

            self.errorGenerated.emit(error_text)

    def stop(self):
        self.__stop = True


# STT
def check_microphone_access():
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=DEFAULT_TOKEN_CHUNK_SIZE,
        )
        stream.close()
        audio.terminate()
        return True
    except Exception as e:
        return False


class RecorderThread(QThread):
    recording_finished = Signal(str)
    errorGenerated = Signal(str)

    # Silence detection parameters
    def __init__(
        self, is_silence_detection=False, silence_duration=3, silence_threshold=500
    ):
        super().__init__()
        self.__stop = False
        self.__is_silence_detection = is_silence_detection
        if self.__is_silence_detection:
            self.__silence_duration = (
                silence_duration  # Duration to detect silence (in seconds)
            )
            self.__silence_threshold = (
                silence_threshold  # Amplitude threshold for silence
            )

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            chunk = 1024  # Record in chunks of 1024 samples
            sample_format = pyaudio.paInt16  # 16 bits per sample
            channels = 2
            fs = 44100  # Record at 44100 samples per second

            p = pyaudio.PyAudio()  # Create an interface to PortAudio

            stream = p.open(
                format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True,
            )

            frames = []  # Initialize array to store frames

            silence_start_time = None  # Track silence start time

            while True:
                if self.__stop:
                    break

                data = stream.read(chunk)
                frames.append(data)

                if self.__is_silence_detection:
                    # Convert the data to a numpy array for amplitude analysis
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    amplitude = np.max(np.abs(audio_data))

                    if amplitude < self.__silence_threshold:
                        # If silent, check if the silence duration threshold is reached
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif (
                            time.time() - silence_start_time >= self.__silence_duration
                        ):
                            break
                    else:
                        # Reset silence start time if sound is detected
                        silence_start_time = None

            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                filename = tmpfile.name

            # Save the recorded data as a WAV file in the temporary file
            wf = wave.open(filename, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b"".join(frames))
            wf.close()

            self.recording_finished.emit(filename)
        except Exception as e:
            if str(e).find("-9996") != -1:
                self.errorGenerated.emit(
                    "No valid input device found. Please connect a microphone or check your audio device settings."
                )
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
                model=STT_MODEL, file=Path(self.filename)
            )
            self.stt_finished.emit(transcript.text)
        except Exception as e:
            # TODO LANGUAGE
            self.errorGenerated.emit(
                f'<p style="color:red">{e}\n\n'
                f"(Are you registered valid OpenAI API Key? This feature requires OpenAI API Key.)</p>"
            )
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

    def __init__(
        self, input_args, info: ChatMessageContainer, is_g4f=False, provider=""
    ):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False
        self.__is_g4f = is_g4f
        self.__provider = provider

        self.__info = info
        self.__info.role = "assistant"

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            self.__info.is_g4f = self.__is_g4f
            # For getting the provider if it is G4F
            get_content_only = not self.__info.is_g4f

            if self.__input_args["stream"]:
                response = get_response(
                    self.__input_args, self.__is_g4f, get_content_only, self.__provider
                )
                for chunk in response:
                    # Get provider if it is G4F
                    # Get the content from choices[0].delta.content if it is G4F, otherwise get it from chunk
                    # The reason is that G4F has content in choices[0].delta.content, otherwise it has content in chunk.
                    if self.__is_g4f:
                        self.__info.provider = chunk.provider
                        self.__info.model = chunk.model
                        chunk = chunk.choices[0].delta.content
                    if self.__stop:
                        self.__info.finish_reason = "stopped by user"
                        self.streamFinished.emit(self.__info)
                        break
                    else:
                        self.replyGenerated.emit(chunk, True, self.__info)
            else:
                response = get_response(
                    self.__input_args, self.__is_g4f, get_content_only
                )
                # Get provider if it is G4F
                # Get the content from choices[0].message.content if it is G4F, otherwise get it from response
                # The reason is that G4F has content in choices[0].message.content, otherwise it has content in response.
                if self.__is_g4f:
                    self.__info.content = response.choices[0].message.content
                    self.__info.model = response.model
                    self.__info.provider = response.provider
                else:
                    self.__info.content = response
                self.__info.prompt_tokens = ""
                self.__info.completion_tokens = ""
                self.__info.total_tokens = ""

            self.__info.finish_reason = "stop"

            if self.__input_args["stream"]:
                self.streamFinished.emit(self.__info)
            else:
                self.replyGenerated.emit(self.__info.content, False, self.__info)
        except Exception as e:
            self.__info.provider = self.__provider
            self.__info.finish_reason = "Error"
            self.__info.content = f'<p style="color:red">{e}</p>'
            if self.__is_g4f:
                # TODO LANGUAGE
                self.__info.content += """\n
You can try the following:

- Change the provider
- Change the model
- Use API instead of G4F
"""
            self.replyGenerated.emit(self.__info.content, False, self.__info)


# To manage only one TTS stream at a time
current_tts_thread = None


def stop_existing_tts_thread():
    if pyqt_openai.util.common.current_tts_thread:
        pyqt_openai.util.common.current_tts_thread.stop()
        pyqt_openai.util.common.current_tts_thread = None


def stream_to_speakers(voice_provider, input_args):
    stop_existing_tts_thread()

    stream_thread = TTSThread(voice_provider, input_args)
    pyqt_openai.util.common.current_tts_thread = stream_thread
    return stream_thread
