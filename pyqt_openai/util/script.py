import base64
import os
import random
import re
import string
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pandas
import requests
from jinja2 import Template
from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QMessageBox

from pyqt_openai import INI_FILE_NAME, DB_FILE_NAME, DEFAULT_FONT_SIZE, DEFAULT_FONT_FAMILY, MAIN_INDEX, \
    PROMPT_NAME_REGEX
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import DB


def get_generic_ext_out_of_qt_ext(text):
    pattern = r'\((\*\.(.+))\)'
    match = re.search(pattern, text)
    extension = '.' + match.group(2) if match.group(2) else ''
    return extension

def open_directory(path):
    if sys.platform.startswith('darwin'):  # macOS
        os.system('open "{}"'.format(path))
    elif sys.platform.startswith('win'):  # Windows
        os.system('start "" "{}"'.format(path))
    elif sys.platform.startswith('linux'):  # Linux
        os.system('xdg-open "{}"'.format(path))
    else:
        print("Unsupported operating system.")

def message_list_to_txt(db, thread_id, title, username='User', ai_name='AI'):
    content = ''
    certain_thread_filename_content = db.selectCertainThreadMessagesRaw(thread_id)
    content += f'== {title} ==' + '\n'*2
    for unit in certain_thread_filename_content:
        unit_prefix = username if unit[2] == 1 else ai_name
        unit_content = unit[3]
        content += f'{unit_prefix}: {unit_content}' + '\n'*2
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

def get_font():
    settings = QSettings(INI_FILE_NAME, QSettings.Format.IniFormat)
    font_family = settings.value("font_family", DEFAULT_FONT_FAMILY, type=str)
    font_size = settings.value("font_size", DEFAULT_FONT_SIZE, type=int)
    return {
        'font_family': font_family,
        'font_size': font_size
    }

def restart_app(settings=None):
    if settings:
        # Save before restart
        settings.sync()
    # Define the arguments to be passed to the executable
    args = [sys.executable, MAIN_INDEX]
    # Call os.execv() to execute the new process
    os.execv(sys.executable, args)

def show_message_box(title, text):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
    result = msg_box.exec()
    return result

def get_conversation_from_chatgpt(filename, most_recent_n:int = None):
    conversations_df = pandas.read_json(filename)
    conv_arr = []
    count = conversations_df.shape[0] if most_recent_n is None else most_recent_n
    for i in range(count):
        conv = conversations_df.iloc[i]
        conv_dict = {}
        name = conv.title
        insert_dt = str(conv.create_time).split('.')[0]
        update_dt = str(conv.update_time).split('.')[0]
        conv_dict['id'] = conv.id
        conv_dict['name'] = name
        conv_dict['insert_dt'] = insert_dt
        conv_dict['update_dt'] = update_dt
        conv_dict['mapping'] = conv.mapping
        conv_arr.append(conv_dict)
    return {
        'columns': ['id', 'name', 'insert_dt', 'update_dt'],
        'data': conv_arr
    }

def get_chatgpt_data(conv_arr):
    for conv in conv_arr:
        # role
        # content
        # insert_dt
        # update_dt
        # model
        conv['messages'] = []
        for k, v in conv['mapping'].items():
            obj = {}
            # We need the create_time, update_time, role, content_type, and content
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

                # print(f'content: {content}')
                if role == 'user':
                    content_parts = '\n'.join(content['parts'])
                    obj['content'] = content_parts
                    conv['messages'].append(obj)
                else:
                    if role == 'tool':
                        # Tool is used for the internal use of the system of OpenAI
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
    exists_f = True if (True if m else False) and DB.selectCertainPromptGroup(name=text) else False
    return exists_f

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

