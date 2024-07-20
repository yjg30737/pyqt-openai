# APP

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

## PROFILE IMAGE & FONT & ICON
DEFAULT_ICON_SIZE = (24, 24)
DEFAULT_USER_IMAGE_PATH = 'ico/user.png'
DEFAULT_AI_IMAGE_PATH = 'ico/openai.png'
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_FAMILY = 'Arial'
FONT_FAMILY_FOR_SOURCE = 'Courier'

## PROMPT
PROMPT_BEGINNING_KEY_NAME = 'prompt_beginning'
PROMPT_JSON_KEY_NAME = 'prompt_json'
PROMPT_MAIN_KEY_NAME = 'prompt_main'
PROMPT_END_KEY_NAME = 'prompt_ending'
INDENT_SIZE = 4

## ETC
COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE = ['id']
PAYPAL_URL = 'https://paypal.me/yjg30737'
BUYMEACOFFEE_URL = 'https://www.buymeacoffee.com/yjg30737'

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

