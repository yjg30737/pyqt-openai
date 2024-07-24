"""
This file is used to store the constants and the global variables that are used throughout the application.
"""


import toml

SETUP_FILENAME = '../pyproject.toml'

with open(SETUP_FILENAME, "r") as file:
    pyproject_data = toml.load(file)

# For the sake of following the PEP8 standard, we will declare module-level dunder names.
# PEP8 standard about dunder names: https://peps.python.org/pep-0008/#module-level-dunder-names

__version__ = pyproject_data["project"]["version"]
__author__ = pyproject_data["project"]["authors"][0]['name']

# Constants
# ----------------------------
# APP
APP_NAME = 'pyqt-openai'
APP_ICON = 'icon.png'
CONTACT = 'yjg30737@gmail.com'
APP_INITIAL_WINDOW_SIZE = (1280, 768)
LICENSE_URL = 'https://github.com/yjg30737/pyqt-openai/blob/main/LICENSE'
PAYPAL_URL = 'https://paypal.me/yjg30737'
BUYMEACOFFEE_URL = 'https://www.buymeacoffee.com/yjg30737'
GITHUB_URL = 'https://github.com/yjg30737/pyqt-openai'
DISCORD_URL = 'https://discord.gg/cHekprskVE'
COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE = ['id']
DEFAULT_LANGUAGE = 'en_US'
LANGUAGE_FILE = 'translations.json'
LANGUAGE_DICT = {
    "English": "en_US",
    "Spanish": "es_ES",
    "Chinese": "zh_CN",
    "Russian": "ru_RU",
    "Korean": "ko_KR",
    "French": "fr_FR",
    "German": "de_DE",
    "Italian": "it_IT",
    "Hindi": "hi_IN",
    "Arabic": "ar_AE",
    "Japanese": "ja_JP",
    "Bengali": "bn_IN",
    "Urdu": "ur_PK",
    "Indonesian": "id_ID",
    "Portuguese": "pt_BR"
}

## PROFILE IMAGE & FONT & ICON
DEFAULT_ICON_SIZE = (24, 24)
DEFAULT_USER_IMAGE_PATH = 'ico/user.png'
DEFAULT_AI_IMAGE_PATH = 'ico/openai.png'
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_FAMILY = 'Arial'
FONT_FAMILY_FOR_SOURCE = 'Courier'

## SHORTCUT
SHORTCUT_GENERAL_ACTION = 'Enter'
SHORTCUT_FIND_PREV = 'Ctrl+Shift+D'
SHORTCUT_FIND_NEXT = 'Ctrl+D'
SHORTCUT_FIND_CLOSE = 'Escape'
SHORTCUT_PROMPT_BEGINNING = 'Ctrl+B'
SHORTCUT_PROMPT_ENDING = 'Ctrl+E'
SHORTCUT_SUPPORT_PROMPT_COMMAND = 'Ctrl+Shift+P'
SHORTCUT_FULL_SCREEN = 'F11'

## DIRECTORY PATH & FILE'S NAME
MAIN_INDEX = 'main.py'
IMAGE_DEFAULT_SAVE_DIRECTORY = 'image_result'
LLAMA_INDEX_DEFAULT_READ_DIRECTORY = './example'
INI_FILE_NAME = 'pyqt_openai.ini'
DB_FILE_NAME = 'conv'

## EXTENSIONS
IMAGE_FILE_EXT = 'Image File (*.jpg *.png)'
TEXT_FILE_EXT = 'Text File (*.txt)'
READ_FILE_EXT = f'{TEXT_FILE_EXT};;{IMAGE_FILE_EXT}'

## PROMPT
PROMPT_BEGINNING_KEY_NAME = 'prompt_beginning'
PROMPT_JSON_KEY_NAME = 'prompt_json'
PROMPT_MAIN_KEY_NAME = 'prompt_main'
PROMPT_END_KEY_NAME = 'prompt_ending'
INDENT_SIZE = 4

# DB

DB_NAME_REGEX = '[a-zA-Z0-9]{1,20}'

THREAD_TABLE_NAME_OLD = 'conv_tb'
THREAD_TRIGGER_NAME_OLD = 'conv_tr'
MESSAGE_TABLE_NAME_OLD = 'conv_unit_tb'

THREAD_TABLE_NAME = 'thread_tb'
THREAD_TRIGGER_NAME = 'thread_tr'
MESSAGE_TABLE_NAME = 'message_tb'

IMAGE_TABLE_NAME = 'image_tb'

THREAD_MESSAGE_INSERTED_TR_NAME_OLD = 'conv_tb_updated_by_unit_inserted_tr'
THREAD_MESSAGE_UPDATED_TR_NAME_OLD = 'conv_tb_updated_by_unit_updated_tr'
THREAD_MESSAGE_DELETED_TR_NAME_OLD = 'conv_tb_updated_by_unit_deleted_tr'

THREAD_MESSAGE_INSERTED_TR_NAME = 'thread_message_inserted_tr'
THREAD_MESSAGE_UPDATED_TR_NAME = 'thread_message_updated_tr'
THREAD_MESSAGE_DELETED_TR_NAME = 'thread_message_deleted_tr'

THREAD_ORDERBY = 'update_dt'

PROPERTY_PROMPT_GROUP_TABLE_NAME = 'prop_prompt_grp_tb'
PROPERTY_PROMPT_UNIT_TABLE_NAME = 'prop_prompt_unit_tb'
TEMPLATE_PROMPT_GROUP_TABLE_NAME = 'template_prompt_grp_tb'
TEMPLATE_PROMPT_TABLE_NAME = 'template_prompt_tb'
PROPERTY_PROMPT_UNIT_DEFAULT_VALUE = [{'name': 'Task', 'text': ''},
                                      {'name': 'Topic', 'text': ''},
                                      {'name': 'Style', 'text': ''},
                                      {'name': 'Tone', 'text': ''},
                                      {'name': 'Audience', 'text': ''},
                                      {'name': 'Length', 'text': ''},
                                      {'name': 'Form', 'text': ''}]

# DEFAULT JSON FILENAME FOR PROMPT
AWESOME_CHATGPT_PROMPTS_FILENAME = 'prompt_res/awesome_chatgpt_prompts.json'
ALEX_BROGAN_PROMPT_FILENAME = 'prompt_res/alex_brogan.json'

import json

# Load the default prompt
AWESOME_CHATGPT_PROMPTS = json.load(open(AWESOME_CHATGPT_PROMPTS_FILENAME))
ALEX_BROGAN_PROMPT = json.load(open(ALEX_BROGAN_PROMPT_FILENAME))

# Update the __all__ list with the PEP8 standard dunder names
__all__ = ['__version__',
           '__author__']

# Update the __all__ list with the constants
__all__.extend([name for name, value in globals().items() if name.isupper()])