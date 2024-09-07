"""
This file includes utility functions that are used in various parts of the application.
Mostly, these functions are used to perform common tasks such as opening a directory, generating random strings, etc.
Some of the functions are used to set PyQt settings, restart the application, show message boxes, etc.
"""


import base64
import json
import os
import random
import re
import string
import sys
import traceback
import zipfile
from datetime import datetime
from pathlib import Path
import winreg
import requests

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QFrame
from jinja2 import Template

from pyqt_openai import MAIN_INDEX, \
    PROMPT_NAME_REGEX, PROMPT_MAIN_KEY_NAME, PROMPT_BEGINNING_KEY_NAME, \
    PROMPT_END_KEY_NAME, PROMPT_JSON_KEY_NAME, CONTEXT_DELIMITER, THREAD_ORDERBY, DEFAULT_APP_NAME, \
    AUTOSTART_REGISTRY_KEY
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import DB


def get_generic_ext_out_of_qt_ext(text):
    pattern = r'\((\*\.(.+))\)'
    match = re.search(pattern, text)
    extension = '.' + match.group(2) if match.group(2) else ''
    return extension

def open_directory(path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))

def message_list_to_txt(db, thread_id, title, username='User', ai_name='AI'):
    content = ''
    certain_thread_filename_content = db.selectCertainThreadMessagesRaw(thread_id)
    content += f'== {title} ==' + CONTEXT_DELIMITER
    for unit in certain_thread_filename_content:
        unit_prefix = username if unit[2] == 1 else ai_name
        unit_content = unit[3]
        content += f'{unit_prefix}: {unit_content}' + CONTEXT_DELIMITER
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
    template = Template('''
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
    ''')
    html = template.render(title=title, chat_history=chat_history)
    return html


def add_file_to_zip(file_content, file_name, output_zip_file):
    with zipfile.ZipFile(output_zip_file, 'a') as zipf:
        zipf.writestr(file_name, file_content)

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def get_image_filename_for_saving(arg: ImagePromptContainer):
    ext = '.png'
    filename_prompt_prefix = '_'.join(''.join(re.findall('[a-zA-Z0-9\\s]', arg.prompt[:20])).split(' '))
    size = f"{arg.width}x{arg.height}"
    filename = '_'.join(map(str, [filename_prompt_prefix, size])) + '_' + generate_random_string(8) + ext

    return filename

def get_image_prompt_filename_for_saving(directory, filename):
    txt_filename = os.path.join(directory, Path(filename).stem + '.txt')
    return txt_filename

def download_image_as_base64(url: str):
    response = requests.get(url)
    response.raise_for_status()  # Check if the URL is correct and raise an exception if there is a problem
    image_data = response.content
    base64_encoded = base64.b64decode(base64.b64encode(image_data).decode('utf-8'))
    return base64_encoded

def restart_app():
    # Define the arguments to be passed to the executable
    args = [sys.executable, MAIN_INDEX]
    # Call os.execv() to execute the new process
    os.execv(sys.executable, args)

def show_message_box_after_change_to_restart(change_list):
    title = LangClass.TRANSLATIONS['Application Restart Required']
    text = LangClass.TRANSLATIONS[
        'The program needs to be restarted because of following changes']
    text += '\n\n' + '\n'.join(change_list) + '\n\n'
    text += LangClass.TRANSLATIONS['Would you like to restart it?']

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
    result = msg_box.exec()
    return result

def get_chatgpt_data_for_preview(filename, most_recent_n:int = None):
    data = json.load(open(filename, 'r'))
    conv_arr = []
    for i in range(len(data)):
        conv = data[i]
        conv_dict = {}
        name = conv['title']
        insert_dt = datetime.fromtimestamp(conv['create_time']).strftime('%Y-%m-%d %H:%M:%S') if conv['create_time'] else None
        update_dt = datetime.fromtimestamp(conv['update_time']).strftime('%Y-%m-%d %H:%M:%S') if conv['update_time'] else None
        conv_dict['id'] = conv['id']
        conv_dict['name'] = name
        conv_dict['insert_dt'] = insert_dt
        conv_dict['update_dt'] = update_dt
        conv_dict['mapping'] = conv['mapping']
        conv_arr.append(conv_dict)

    conv_arr = sorted(conv_arr, key=lambda x: x[THREAD_ORDERBY], reverse=True)
    if most_recent_n is not None:
        conv_arr = conv_arr[:most_recent_n]

    return {
        'columns': ['id', 'name', 'insert_dt', 'update_dt'],
        'data': conv_arr
    }

def get_chatgpt_data_for_import(conv_arr):
    for conv in conv_arr:
        conv['messages'] = []
        for k, v in conv['mapping'].items():
            obj = {}
            message = v['message']
            if message:
                metadata = message['metadata']

                role = message['author']['role']
                create_time = datetime.fromtimestamp(message['create_time']).strftime('%Y-%m-%d %H:%M:%S') if message['create_time'] else None
                update_time = datetime.fromtimestamp(message['update_time']).strftime('%Y-%m-%d %H:%M:%S') if message['update_time'] else None
                content = message['content']

                obj['role'] = role
                obj['insert_dt'] = create_time
                obj['update_dt'] = update_time

                if role == 'user':
                    content_parts = '\n'.join([str(c) for c in content['parts']])
                    obj['content'] = content_parts
                    conv['messages'].append(obj)
                else:
                    if role == 'tool':
                        pass
                    elif role == 'assistant':
                        model_slug = metadata.get('model_slug', None)
                        obj['model'] = model_slug
                        content_type = content['content_type']
                        # Text (General chat)
                        if content_type == 'text':
                            content_parts = '\n'.join(content['parts'])
                            obj['content'] = content_parts
                            conv['messages'].append(obj)
                        elif content_type == 'code':
                            # Currently there is no way to apply every aspect of the "code" content_type into the code.
                            # So let it be for now.
                            pass

                            # image: content: dict_keys(['content_type', 'language', 'response_format_name', 'text'])
                            # language = content['language']
                            # response_format_name = content['response_format_name']
                            # print(f'language: {language}')
                            # print(f'response_format_name: {response_format_name}')
                            # print(f'content: {content["text"]}')
                    elif role == 'system':
                        # Won't use the system
                        pass
    # Remove mapping keys
    for conv in conv_arr:
        del conv['mapping']

    return conv_arr

def is_prompt_group_name_valid(text):
    """
    Check if the prompt group name is valid or not and exists in the database
    :param text: The text to check
    """
    m = re.search(PROMPT_NAME_REGEX, text)
    # Check if the prompt group with same name already exists
    if DB.selectCertainPromptGroup(name=text):
        return False
    return True if m else False

def is_prompt_entry_name_valid(group_id, text):
    """
    Check if the prompt entry name is valid or not and exists in the database
    :param group_id: The group id to check
    :param text: The text to check
    """
    m = re.search(PROMPT_NAME_REGEX, text)
    # Check if the prompt entry with same name already exists
    exists_f = True if (True if m else False) and DB.selectPromptEntry(group_id=group_id, name=text) else False
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
        if 'name' not in item or 'data' not in item:
            return False

        # Check if 'name' is not empty
        if not item['name']:
            return False

        # Check if 'data' is a list
        if not isinstance(item['data'], list):
            return False

        # Iterate through each data item in 'data' list
        for data_item in item['data']:
            # Check if data_item is a dictionary
            if not isinstance(data_item, dict):
                return False

            # Check if 'name' and 'content' keys exist in data_item
            if 'name' not in data_item or 'content' not in data_item:
                return False

            # Check if 'name' in data_item is not empty
            if not data_item['name']:
                return False

    return True

def get_prompt_data(prompt_type='form'):
    data = []
    for group in DB.selectPromptGroup(prompt_type=prompt_type):
        group_obj = {
            'name': group.name,
            'data': []
        }
        for entry in DB.selectPromptEntry(group.id):
            group_obj['data'].append({
                'name': entry.name,
                'content': entry.content
            })
        data.append(group_obj)
    return data

def showJsonSample(json_sample_widget, json_sample):
    json_sample_widget.setText(json_sample)
    json_sample_widget.setReadOnly(True)
    json_sample_widget.setMinimumSize(600, 350)
    json_sample_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    json_sample_widget.setWindowTitle(LangClass.TRANSLATIONS['JSON Sample'])
    json_sample_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    json_sample_widget.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowStaysOnTopHint)
    json_sample_widget.show()

def get_content_of_text_file_for_send(filenames: list[str]):
    """
    Get the content of the text file for sending to the AI
    :param filenames: The list of filenames to get the content from
    :return: The content of the text file
    """
    source_context = ''
    for filename in filenames:
        base_filename = os.path.basename(filename)
        source_context += f'=== {base_filename} start ==='
        source_context += CONTEXT_DELIMITER
        with open(filename, 'r', encoding='utf-8') as f:
            source_context += f.read()
        source_context += CONTEXT_DELIMITER
        source_context += f'=== {base_filename} end ==='
        source_context += CONTEXT_DELIMITER
    prompt_context = f'== Source Start ==\n{source_context}== Source End =='
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

    if direction == 'up':
        switch_focus(PROMPT_MAIN_KEY_NAME, PROMPT_BEGINNING_KEY_NAME)
        switch_focus(PROMPT_END_KEY_NAME, PROMPT_JSON_KEY_NAME)
        switch_focus(PROMPT_END_KEY_NAME, PROMPT_MAIN_KEY_NAME)
        switch_focus(PROMPT_JSON_KEY_NAME, PROMPT_MAIN_KEY_NAME)
    elif direction == 'down':
        switch_focus(PROMPT_BEGINNING_KEY_NAME, PROMPT_MAIN_KEY_NAME)
        switch_focus(PROMPT_MAIN_KEY_NAME, PROMPT_JSON_KEY_NAME)
        switch_focus(PROMPT_MAIN_KEY_NAME, PROMPT_END_KEY_NAME)
        switch_focus(PROMPT_JSON_KEY_NAME, PROMPT_END_KEY_NAME)
    else:
        print('Invalid direction:', direction)

def getSeparator(orientation='horizontal'):
    sep = QFrame()
    if orientation == 'horizontal':
        sep.setFrameShape(QFrame.Shape.HLine)
    elif orientation == 'vertical':
        sep.setFrameShape(QFrame.Shape.VLine)
    else:
        raise ValueError('Invalid orientation')
    sep.setFrameShadow(QFrame.Shadow.Sunken)
    return sep

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler.
    This should be only used in release mode.
    """
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Unhandled exception: {error_msg}")

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText("An unexpected error occurred.")
    msg_box.setInformativeText(error_msg)
    msg_box.setWindowTitle("Error")
    msg_box.exec_()


# Set auto start on Windows
def is_auto_start_enabled_windows():
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REGISTRY_KEY, 0,
                         winreg.KEY_READ)
    try:
        winreg.QueryValueEx(key, DEFAULT_APP_NAME)
        return True
    except FileNotFoundError:
        return False

def set_auto_start_windows(enable: bool):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_REGISTRY_KEY, 0, winreg.KEY_WRITE)

    if enable:
        exe_path = sys.executable  # 현재 실행 파일 경로
        winreg.SetValueEx(key, DEFAULT_APP_NAME, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, DEFAULT_APP_NAME)
        except FileNotFoundError:
            pass