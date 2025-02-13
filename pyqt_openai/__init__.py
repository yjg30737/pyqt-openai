"""This file is used to store the constants and the global constants / variables that are used throughout the application.
Constants/Variables that are stored here are used throughout the application for the following purposes:
- Initial values related to the environment settings
- Values used internally within the application (e.g., application name, DB name, table name, etc.)
- Values related to the design and UI of the application
- Default LLM list for the application settings.

Constants/Variables that are stored here are not supposed to be changed during the runtime except for __init__.py.
Variables which are used globally and can be changed are stored in globals.py.
"""

import json
import os
import shutil
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent  # VividNode/pyqt_openai
ROOT_DIR = SRC_DIR.parent  # VividNode

# For the sake of following the PEP8 standard, we will declare module-level dunder names.
# PEP8 standard about dunder names: https://peps.python.org/pep-0008/#module-level-dunder-names

__version__ = "1.9.0"
__author__ = "Jung Gyu Yoon"

# Constants
# ----------------------------
# APP
PACKAGE_NAME = "pyqt-openai"
OWNER = "yjg30737"

DEFAULT_APP_NAME = "VividNode"

# For Windows
AUTOSTART_REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


# Check if the application is frozen (compiled with PyInstaller)
# If this is main.py, it will return False, that means it is not frozen.
def is_frozen():
    return hasattr(sys, "frozen")


# The executable path of the application
def get_executable_path():
    if is_frozen():  # For PyInstaller
        executable_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    else:
        executable_path = os.path.dirname(os.path.abspath(__file__))
    return executable_path


EXEC_PATH = get_executable_path()

# The current filename of the application
CURRENT_FILENAME = os.path.join(EXEC_PATH, f"{DEFAULT_APP_NAME}.exe")


def get_config_directory():
    if os.name == "nt":  # Windows
        config_dir = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), DEFAULT_APP_NAME)
    elif os.name == "posix":  # macOS/Linux
        config_dir = os.path.join(
            os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
            DEFAULT_APP_NAME,
        )
    else:
        config_dir = os.path.expanduser(f"~/.{DEFAULT_APP_NAME}")  # Fallback

    # Ensure the directory exists
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    return config_dir


BIN_DIR = get_config_directory()

UPDATER_NAME = "Updater.exe" if sys.platform == "win32" else "Updater"

# The default updater path (relative to the application's root directory) - For Windows
UPDATER_PATH = os.path.join(BIN_DIR, UPDATER_NAME)


# Move the binary file to the config folder to prevent "file not found" error
def move_bin(filename, dst_dir):
    original_path = os.path.join(ROOT_DIR, filename)
    if os.path.exists(original_path):
        if os.path.exists(dst_dir):
            os.remove(dst_dir)
        shutil.move(original_path, dst_dir)


move_bin(UPDATER_NAME, UPDATER_PATH)

CONTACT = "yjg30737@gmail.com"
APP_INITIAL_WINDOW_SIZE = (1280, 768)

TRANSPARENT_RANGE = 20, 100
TRANSPARENT_INIT_VAL = 100

LARGE_LABEL_PARAM = ("Arial", 32)
MEDIUM_LABEL_PARAM = ("Arial", 16)
SMALL_LABEL_PARAM = ("Arial", 10)

LICENSE = "MIT"
LICENSE_URL = "https://github.com/yjg30737/pyqt-openai/blob/main/LICENSE"
KOFI_URL = "https://ko-fi.com/junggyuyoon"
PATREON_URL = "https://patreon.com/user?u=121090702"
PAYPAL_URL = "https://paypal.me/yjg30737"
GITHUB_URL = "https://github.com/yjg30737/pyqt-openai"
DISCORD_URL = "https://discord.gg/cHekprskVE"

QUICKSTART_MANUAL_URL = (
    "https://medium.com/@yjg30737/what-is-vividnode-how-to-use-it-4d8a9269a3c0"
)
LLAMAINDEX_URL = "https://medium.com/@yjg30737/what-is-llamaindex-9b821d66568f"
HOW_TO_GET_OPENAI_API_KEY_URL = (
    "https://medium.com/@yjg30737/how-to-get-your-openai-api-key-e2193850932e"
)
HOW_TO_EXPORT_CHATGPT_CONVERSATION_HISTORY_URL = "https://medium.com/@yjg30737/how-to-export-your-chatgpt-conversation-history-caa0946d6349"
HOW_TO_REPLICATE = "https://medium.com/@yjg30737/10a2cb983ceb"
HOW_TO_GET_CLAUDE_API_KEY_URL = "https://medium.com/@yjg30737/how-to-get-started-with-claude-api-step-by-step-guide-92b5e35ae0a0"
HOW_TO_GET_GEMINI_API_KEY_URL = "https://medium.com/@yjg30737/e61a84d64c69"
REPORT_ERROR_URL = (
    "https://github.com/yjg30737/pyqt-openai?tab=readme-ov-file#troubleshooting"
)

AWESOME_CHATGPT_PROMPTS_URL = "https://huggingface.co/datasets/fka/awesome-chatgpt-prompts/tree/main"

COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_CHAT = ["id"]
COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_IMAGE = ["id", "data"]
DEFAULT_LANGUAGE = "en_US"
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
    "Portuguese": "pt_BR",
}

MESSAGE_PADDING = 16
MESSAGE_MAXIMUM_HEIGHT = 800
MESSAGE_MAXIMUM_HEIGHT_RANGE = 300, 1000

CONTEXT_DELIMITER = "\n" * 2
PROMPT_IMAGE_SCALE = 200, 200
TOAST_DURATION = 3

## ICONS
ICON_PATH = os.path.join(EXEC_PATH, "ico")

DEFAULT_APP_ICON = os.path.join(EXEC_PATH, "icon.ico")

ICON_ADD = os.path.join(ICON_PATH, "add.svg")
ICON_CASE = os.path.join(ICON_PATH, "case.svg")
ICON_CLOSE = os.path.join(ICON_PATH, "close.svg")
ICON_COPY = os.path.join(ICON_PATH, "copy.svg")
ICON_CUSTOMIZE = os.path.join(ICON_PATH, "customize.svg")
ICON_DELETE = os.path.join(ICON_PATH, "delete.svg")
ICON_DISCORD = os.path.join(ICON_PATH, "discord.svg")
ICON_EXPORT = os.path.join(ICON_PATH, "export.svg")
ICON_FAVORITE_NO = os.path.join(ICON_PATH, "favorite_no.svg")
ICON_FAVORITE_YES = os.path.join(ICON_PATH, "favorite_yes.svg")
ICON_FOCUS_MODE = os.path.join(ICON_PATH, "focus_mode.svg")
ICON_FULLSCREEN = os.path.join(ICON_PATH, "fullscreen.svg")
ICON_UPDATE = os.path.join(ICON_PATH, "update.svg")
ICON_GITHUB = os.path.join(ICON_PATH, "github.svg")
ICON_HELP = os.path.join(ICON_PATH, "help.svg")
ICON_HISTORY = os.path.join(ICON_PATH, "history.svg")
ICON_IMPORT = os.path.join(ICON_PATH, "import.svg")
ICON_INFO = os.path.join(ICON_PATH, "info.svg")
ICON_NEXT = os.path.join(ICON_PATH, "next.svg")
ICON_OPENAI = os.path.join(ICON_PATH, "openai.png")
ICON_PREV = os.path.join(ICON_PATH, "prev.svg")
ICON_PROMPT = os.path.join(ICON_PATH, "prompt.svg")
ICON_QUESTION = os.path.join(ICON_PATH, "question.svg")
ICON_REFRESH = os.path.join(ICON_PATH, "refresh.svg")
ICON_REGEX = os.path.join(ICON_PATH, "regex.svg")
ICON_SAVE = os.path.join(ICON_PATH, "save.svg")
ICON_SEARCH = os.path.join(ICON_PATH, "search.svg")
ICON_SETTING = os.path.join(ICON_PATH, "setting.svg")
ICON_SIDEBAR = os.path.join(ICON_PATH, "sidebar.svg")
ICON_STACKONTOP = os.path.join(ICON_PATH, "stackontop.svg")
ICON_USER = os.path.join(ICON_PATH, "user.png")
ICON_VERTICAL_THREE_DOTS = os.path.join(ICON_PATH, "vertical_three_dots.svg")
ICON_WORD = os.path.join(ICON_PATH, "word.svg")
ICON_SEND = os.path.join(ICON_PATH, "send.svg")
ICON_RECORD = os.path.join(ICON_PATH, "record.svg")
ICON_SPEAKER = os.path.join(ICON_PATH, "speaker.svg")
ICON_PAYPAL = os.path.join(ICON_PATH, "paypal.png")
ICON_KOFI = os.path.join(ICON_PATH, "kofi.png")
ICON_PATREON = os.path.join(ICON_PATH, "patreon.svg")
ICON_SHORTCUT = os.path.join(ICON_PATH, "shortcut.svg")
ICON_REALTIME_API = os.path.join(ICON_PATH, "realtime_api.svg")
ICON_FILE = os.path.join(ICON_PATH, "file.svg")

## IMAGE
IMAGE_PATH = os.path.join(EXEC_PATH, "img")

IMAGE_IMPORT_PROMPT_WITH_CSV_RIGHT_FORM = os.path.join(IMAGE_PATH, "import_prompt_with_csv_right_form.png")

## CUSTOMIZE
DEFAULT_ICON_SIZE = (24, 24)
DEFAULT_USER_IMAGE_PATH = ICON_USER
DEFAULT_AI_IMAGE_PATH = ICON_OPENAI
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_FAMILY = "Arial"

DEFAULT_HIGHLIGHT_TEXT_COLOR = "#A2D0DD"
DEFAULT_BUTTON_HOVER_COLOR = "#A2D0DD"
DEFAULT_BUTTON_PRESSED_COLOR = "#B3E0FF"
DEFAULT_BUTTON_CHECKED_COLOR = "#B3E0FF"
DEFAULT_SOURCE_HIGHLIGHT_COLOR = "#CCB500"
DEFAULT_SOURCE_ERROR_COLOR = "#FF0000"
DEFAULT_FOUND_TEXT_COLOR = "#00A2E8"
DEFAULT_FOUND_TEXT_BG_COLOR = "#FFF200"

DEFAULT_LINK_COLOR = "#4F93FF"
DEFAULT_LINK_HOVER_COLOR = "#FF0000"

DEFAULT_TOAST_BACKGROUND_COLOR = "#444444"
DEFAULT_TOAST_FOREGROUND_COLOR = "#EEEEEE"

DEFAULT_WARNING_COLOR = "#FFA500"

## MARKDOWN
# I am not planning to use it at the moment.
# DEFAULT_MARKDOWN_span_font = 'Courier New'
# DEFAULT_MARKDOWN_span_color = '#000'
# DEFAULT_MARKDOWN_ul_color = '#000'
# DEFAULT_MARKDOWN_h1_color = '#000'
# DEFAULT_MARKDOWN_h2_color = '#000'
# DEFAULT_MARKDOWN_h3_color = '#000'
# DEFAULT_MARKDOWN_h4_color = '#000'
# DEFAULT_MARKDOWN_h5_color = '#000'
# DEFAULT_MARKDOWN_h6_color = '#000'
# DEFAULT_MARKDOWN_a_color = '#000'


command_key = "Ctrl"
if sys.platform == "darwin":
    command_key = "Cmd"


## SHORTCUT
DEFAULT_SHORTCUT_GENERAL_ACTION = "Return"
DEFAULT_SHORTCUT_FIND_PREV = f"{command_key}+Shift+D"
DEFAULT_SHORTCUT_FIND_NEXT = f"{command_key}+D"
DEFAULT_SHORTCUT_FIND_CLOSE = "Escape"
DEFAULT_SHORTCUT_PROMPT_BEGINNING = f"{command_key}+B"
DEFAULT_SHORTCUT_PROMPT_ENDING = f"{command_key}+E"
DEFAULT_SHORTCUT_SUPPORT_PROMPT_COMMAND = f"{command_key}+Shift+P"
DEFAULT_SHORTCUT_STACK_ON_TOP = f"{command_key}+Shift+S"
DEFAULT_SHORTCUT_SHOW_SECONDARY_TOOLBAR = f"{command_key}+Shift+T"
DEFAULT_SHORTCUT_FOCUS_MODE = "F10"
DEFAULT_SHORTCUT_FULL_SCREEN = "F11"
DEFAULT_SHORTCUT_FIND = f"{command_key}+F"
DEFAULT_SHORTCUT_JSON_MODE = f"{command_key}+J"
DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW = f"{command_key}+L"
DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW = f"{command_key}+R"
DEFAULT_SHORTCUT_CONTROL_PROMPT_WINDOW = f"{command_key}+Shift+C"
DEFAULT_SHORTCUT_RECORD = f"{command_key}+Shift+R"
DEFAULT_SHORTCUT_SETTING = f"{command_key}+Alt+S"
DEFAULT_SHORTCUT_SEND = f"{command_key}+Return"

DEFAULT_SWITCH_PROMPT_UP = f"{command_key}+Up"
DEFAULT_SWITCH_PROMPT_DOWN = f"{command_key}+Down"


## DIRECTORY PATH & FILE'S NAME
MAIN_INDEX = "main.py"
IMAGE_DEFAULT_SAVE_DIRECTORY = "image_result"
INI_FILE_NAME = os.path.join(get_config_directory(), "config.yaml")
LANGUAGE_FILE_BASE_NAME = "translations.json"
LANGUAGE_FILE = os.path.join(get_config_directory(), LANGUAGE_FILE_BASE_NAME)
LANGUAGE_FILE_SRC = os.path.join(
    os.path.join(EXEC_PATH, "lang"), LANGUAGE_FILE_BASE_NAME,
)

# Make sure the language file exists
if not os.path.exists(LANGUAGE_FILE):
    shutil.copy(LANGUAGE_FILE_SRC, LANGUAGE_FILE)


DB_FILE_NAME = "conv"
FILE_NAME_LENGTH = 32
QFILEDIALOG_DEFAULT_DIRECTORY = os.path.expanduser("~")

## EXTENSIONS
TEXT_FILE_EXT_LIST = [".txt"]
IMAGE_FILE_EXT_LIST = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
IMAGE_FILE_EXT_LIST_STR = "Image File (*.png *.jpg *.jpeg *.gif *.bmp)"
TEXT_FILE_EXT_LIST_STR = "Text File (*.txt)"
JSON_FILE_EXT_LIST_STR = "JSON File (*.json)"
CSV_FILE_EXT_LIST_STR = "CSV File (*.csv)"
READ_FILE_EXT_LIST_STR = f"{TEXT_FILE_EXT_LIST_STR};;{IMAGE_FILE_EXT_LIST_STR}"

## PROMPT
PROMPT_BEGINNING_KEY_NAME = "prompt_beginning"
PROMPT_JSON_KEY_NAME = "prompt_json"
PROMPT_MAIN_KEY_NAME = "prompt_main"
PROMPT_END_KEY_NAME = "prompt_ending"
INDENT_SIZE = 4
NOTIFIER_MAX_CHAR = 100

# DB
DB_NAME_REGEX = "[a-zA-Z0-9]{1,20}"

THREAD_TABLE_NAME_OLD = "conv_tb"
THREAD_TRIGGER_NAME_OLD = "conv_tr"
MESSAGE_TABLE_NAME_OLD = "conv_unit_tb"

CHAT_FILE_TABLE_NAME = "chat_file_tb"

THREAD_TABLE_NAME = "thread_tb"
THREAD_TRIGGER_NAME = "thread_tr"
MESSAGE_TABLE_NAME = "message_tb"

IMAGE_TABLE_NAME = "image_tb"

THREAD_MESSAGE_INSERTED_TR_NAME_OLD = "conv_tb_updated_by_unit_inserted_tr"
THREAD_MESSAGE_UPDATED_TR_NAME_OLD = "conv_tb_updated_by_unit_updated_tr"
THREAD_MESSAGE_DELETED_TR_NAME_OLD = "conv_tb_updated_by_unit_deleted_tr"

THREAD_MESSAGE_INSERTED_TR_NAME = "thread_message_inserted_tr"
THREAD_MESSAGE_UPDATED_TR_NAME = "thread_message_updated_tr"
THREAD_MESSAGE_DELETED_TR_NAME = "thread_message_deleted_tr"

THREAD_ORDERBY = "update_dt"

PROPERTY_PROMPT_GROUP_TABLE_NAME_OLD = "prop_prompt_grp_tb"
PROPERTY_PROMPT_UNIT_TABLE_NAME_OLD = "prop_prompt_unit_tb"
TEMPLATE_PROMPT_GROUP_TABLE_NAME_OLD = "template_prompt_grp_tb"
TEMPLATE_PROMPT_TABLE_NAME_OLD = "template_prompt_tb"
PROPERTY_PROMPT_UNIT_DEFAULT_VALUE = [
    {"name": "Task", "content": ""},
    {"name": "Topic", "content": ""},
    {"name": "Style", "content": ""},
    {"name": "Tone", "content": ""},
    {"name": "Audience", "content": ""},
    {"name": "Length", "content": ""},
    {"name": "Form", "content": ""},
]

PROMPT_GROUP_TABLE_NAME = "prompt_group_tb"
PROMPT_ENTRY_TABLE_NAME = "prompt_entry_tb"


# AI
## OPENAI
OPENAI_REQUEST_URL = "https://api.openai.com/v1/models"

## PARAMETER - OPENAI CHAT
OPENAI_TEMPERATURE_RANGE = 0, 2
OPENAI_TEMPERATURE_STEP = 0.01

MAX_TOKENS_RANGE = 512, 128000

TOP_P_RANGE = 0, 1
TOP_P_STEP = 0.01

FREQUENCY_PENALTY_RANGE = 0, 2
FREQUENCY_PENALTY_STEP = 0.01

PRESENCE_PENALTY_RANGE = 0, 2
PRESENCE_PENALTY_STEP = 0.01

## OPENAI WHISPER (TTS, STT)
WHISPER_TTS_VOICE_TYPE = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
WHISPER_TTS_VOICE_SPEED_RANGE = 0.25, 4.0
WHISPER_TTS_MODEL = "tts-1"

## EDGE-TTS (TTS)
EDGE_TTS_VOICE_TYPE = [
    "en-GB-SoniaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-AvaMultilingualNeural",
]

# TTS in general
TTS_DEFAULT_PROVIDER = "OpenAI"
TTS_DEFAULT_VOICE = "alloy"
TTS_DEFAULT_SPEED = 1.0
TTS_DEFAULT_AUTO_PLAY = False
TTS_DEFAULT_AUTO_STOP_SILENCE_DURATION = 3

STT_MODEL = "whisper-1"

DEFAULT_TOKEN_CHUNK_SIZE = 1024

# This doesn't need endpoint
OPENAI_DEFAULT_IMAGE_MODEL = "dall-e-3"

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# This has to be managed separately since some of the arguments are different with usual models
O1_MODELS = ["o1-preview", "o1-mini"]

# For filtering out famous LLMs for image models
FAMOUS_LLM_LIST = ["gpt", "claude", "gemini", "llama", "meta", "qwen", "falcon"]

# Overall API configuration data
DEFAULT_API_CONFIGS = [
    # OpenAI
    {
        "display_name": "OpenAI",
        "env_var_name": "OPENAI_API_KEY",
        "api_key": "",
        "manual_url": HOW_TO_GET_OPENAI_API_KEY_URL,
        "model_list": ["gpt-4o", "gpt-4o-mini"] + O1_MODELS,
    },
    # Azure
    {
        "display_name": "Azure",
        "env_var_name": "AZURE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure",
    },
    {
        "display_name": "Azure Base",
        "env_var_name": "AZURE_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure",
    },
    {
        "display_name": "Azure Version",
        "env_var_name": "AZURE_API_VERSION",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure",
    },
    {
        "display_name": "Azure AD Token",
        "env_var_name": "AZURE_AD_TOKEN",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure",
    },
    {
        "display_name": "Azure API Type",
        "env_var_name": "AZURE_API_TYPE",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure",
    },
    # Azure AI Studio
    {
        "display_name": "Azure AI",
        "env_var_name": "AZURE_AI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure_ai",
    },
    {
        "display_name": "Azure AI Base",
        "env_var_name": "AZURE_AI_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "azure_ai",
    },
    # Gemini
    {
        "display_name": "Gemini",
        "env_var_name": "GEMINI_API_KEY",
        "api_key": "",
        "manual_url": HOW_TO_GET_GEMINI_API_KEY_URL,
        "prefix": "gemini",
        "model_list": ["gemini/gemini-1.5-flash", "gemini/gemini-1.5-pro"],
    },
    # Anthropic
    {
        "display_name": "Anthropic",
        "env_var_name": "ANTHROPIC_API_KEY",
        "api_key": "",
        "manual_url": HOW_TO_GET_CLAUDE_API_KEY_URL,
        "model_list": ["claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"],
    },
    # AWS Sagemaker
    {
        "display_name": "AWS Access Key",
        "env_var_name": "AWS_ACCESS_KEY_ID",
        "api_key": "",
        "manual_url": "",
        "prefix": "sagemaker",
    },
    {
        "display_name": "AWS Secret Key",
        "env_var_name": "AWS_SECRET_ACCESS_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "sagemaker",
    },
    {
        "display_name": "AWS Region",
        "env_var_name": "AWS_REGION_NAME",
        "api_key": "",
        "manual_url": "",
        "prefix": "sagemaker",
    },
    # AWS Bedrock
    {
        "display_name": "AWS Bedrock Access Key",
        "env_var_name": "AWS_ACCESS_KEY_ID",
        "api_key": "",
        "manual_url": "",
        "prefix": "bedrock",
    },
    {
        "display_name": "AWS Bedrock Secret Key",
        "env_var_name": "AWS_SECRET_ACCESS_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "bedrock",
    },
    {
        "display_name": "AWS Bedrock Region",
        "env_var_name": "AWS_REGION_NAME",
        "api_key": "",
        "manual_url": "",
        "prefix": "bedrock",
    },
    # LiteLLM Proxy
    {
        "display_name": "LiteLLM Proxy",
        "env_var_name": "LITELLM_PROXY_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "litellm_proxy",
    },
    {
        "display_name": "LiteLLM Proxy Base",
        "env_var_name": "LITELLM_PROXY_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "litellm_proxy",
    },
    # Mistral AI API
    {
        "display_name": "Mistral AI",
        "env_var_name": "MISTRAL_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "mistral",
    },
    # Codestral API
    {
        "display_name": "Codestral",
        "env_var_name": "CODESTRAL_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "codestral",
    },
    # Cohere
    {
        "display_name": "Cohere",
        "env_var_name": "COHERE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "cohere",
    },
    # Anyscale
    {
        "display_name": "Anyscale",
        "env_var_name": "ANYSCALE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "anyscale",
    },
    # Huggingface
    {
        "display_name": "Huggingface",
        "env_var_name": "HUGGINGFACE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "huggingface",
    },
    # Databricks
    {
        "display_name": "Databricks",
        "env_var_name": "DATABRICKS_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "databricks",
    },
    {
        "display_name": "Databricks Base",
        "env_var_name": "DATABRICKS_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "databricks",
    },
    # IBM Watsonx
    {
        "display_name": "IBM Watsonx",
        "env_var_name": "WATSONX_URL",
        "api_key": "",
        "manual_url": "",
        "prefix": "watsonx",
    },
    {
        "display_name": "IBM Watsonx API Key",
        "env_var_name": "WATSONX_APIKEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "watsonx",
    },
    {
        "display_name": "IBM Watsonx Token",
        "env_var_name": "WATSONX_TOKEN",
        "api_key": "",
        "manual_url": "",
        "prefix": "watsonx",
    },
    {
        "display_name": "IBM Watsonx Project ID",
        "env_var_name": "WATSONX_PROJECT_ID",
        "api_key": "",
        "manual_url": "",
        "prefix": "watsonx",
    },
    {
        "display_name": "IBM Watsonx Deployment Space",
        "env_var_name": "WATSONX_DEPLOYMENT_SPACE_ID",
        "api_key": "",
        "manual_url": "",
        "prefix": "watsonx",
    },
    # Predibase
    {
        "display_name": "Predibase",
        "env_var_name": "PREDIBASE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "predibase",
    },
    # Nvidia NIM
    {
        "display_name": "Nvidia NIM",
        "env_var_name": "NVIDIA_NIM_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "nvidia_nim",
    },
    # XAI
    {
        "display_name": "XAI",
        "env_var_name": "XAI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "xai",
    },
    # LM Studio
    {
        "display_name": "LM Studio Base",
        "env_var_name": "LM_STUDIO_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "lm_studio",
    },
    {
        "display_name": "LM Studio",
        "env_var_name": "LM_STUDIO_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "lm_studio",
    },
    # Cerebras
    {
        "display_name": "Cerebras",
        "env_var_name": "CEREBRAS_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "cerebras",
    },
    # Volcano Engine (Volcengine)
    {
        "display_name": "Volcengine",
        "env_var_name": "VOLCENGINE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "volcengine",
    },
    # Perplexity AI
    {
        "display_name": "Perplexity AI",
        "env_var_name": "PERPLEXITYAI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "perplexity",
    },
    # FriendliAI
    {
        "display_name": "Friendli Token",
        "env_var_name": "FRIENDLI_TOKEN",
        "api_key": "",
        "manual_url": "",
        "prefix": "friendliai",
    },
    {
        "display_name": "Friendli API Base",
        "env_var_name": "FRIENDLI_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "friendliai",
    },
    # Groq
    {
        "display_name": "Groq",
        "env_var_name": "GROQ_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "groq",
    },
    # Github
    {
        "display_name": "Github",
        "env_var_name": "GITHUB_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "github",
    },
    # Deepseek
    {
        "display_name": "Deepseek",
        "env_var_name": "DEEPSEEK_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "deepseek",
    },
    # Fireworks AI
    {
        "display_name": "Fireworks AI",
        "env_var_name": "FIREWORKS_AI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "fireworks_ai",
    },
    # Clarifai
    {
        "display_name": "Clarifai",
        "env_var_name": "CLARIFAI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "clarifai",
    },
    # Xinference [Xorbits Inference]
    {
        "display_name": "Xinference Base",
        "env_var_name": "XINFERENCE_API_BASE",
        "api_key": "",
        "manual_url": "",
        "prefix": "xinference",
    },
    {
        "display_name": "Xinference",
        "env_var_name": "XINFERENCE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "xinference",
    },
    # Cloudflare Workers AI
    {
        "display_name": "Cloudflare",
        "env_var_name": "CLOUDFLARE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "cloudflare",
    },
    {
        "display_name": "Cloudflare Account",
        "env_var_name": "CLOUDFLARE_ACCOUNT_ID",
        "api_key": "",
        "manual_url": "",
        "prefix": "cloudflare",
    },
    # DeepInfra
    {
        "display_name": "DeepInfra",
        "env_var_name": "DEEPINFRA_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "deepinfra",
    },
    # AI21
    {
        "display_name": "AI21",
        "env_var_name": "AI21_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "ai21",
    },
    # NLP Cloud
    {
        "display_name": "NLP Cloud",
        "env_var_name": "NLP_CLOUD_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "nlp_cloud",
    },
    # Replicate
    {
        "display_name": "Replicate",
        "env_var_name": "REPLICATE_API_KEY",
        "api_key": "",
        "manual_url": HOW_TO_REPLICATE,
        "prefix": "replicate",
    },
    # Together AI
    {
        "display_name": "Together AI",
        "env_var_name": "TOGETHERAI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "together_ai",
    },
    # Voyage AI
    {
        "display_name": "Voyage AI",
        "env_var_name": "VOYAGE_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "voyage",
    },
    # Jina AI
    {
        "display_name": "Jina AI",
        "env_var_name": "JINA_AI_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "jina_ai",
    },
    # Aleph Alpha
    {
        "display_name": "Aleph Alpha",
        "env_var_name": "ALEPHALPHA_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "alephalpha",
    },
    # Baseten
    {
        "display_name": "Baseten",
        "env_var_name": "BASETEN_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "baseten",
    },
    # OpenRouter
    {
        "display_name": "OpenRouter",
        "env_var_name": "OPENROUTER_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "openrouter",
    },
    {
        "display_name": "OpenRouter Site",
        "env_var_name": "OR_SITE_URL",
        "api_key": "",
        "manual_url": "",
        "prefix": "openrouter",
    },
    {
        "display_name": "OpenRouter App Name",
        "env_var_name": "OR_APP_NAME",
        "api_key": "",
        "manual_url": "",
        "prefix": "openrouter",
    },
    # Sambanova
    {
        "display_name": "Sambanova",
        "env_var_name": "SAMBANOVA_API_KEY",
        "api_key": "",
        "manual_url": "",
        "prefix": "sambanova",
    },
]

DEFAULT_LLM = "gpt-4o"

DEFAULT_IMAGE_PROVIDER_LIST = ["openai", "replicate"]

COMBOBOX_SEPARATOR = ['-'*8]

G4F_PROVIDER_DEFAULT = "Auto"

G4F_USE_CHAT_HISTORY = True

G4F_DEFAULT_IMAGE_MODEL = "flux"

# Constants related to the number of messages LLM will store
MAXIMUM_MESSAGES_IN_PARAMETER = 40
MAXIMUM_MESSAGES_IN_PARAMETER_RANGE = 2, 1000

# llamaIndex
LLAMA_INDEX_DEFAULT_SUPPORTED_FORMATS_LIST = [".txt"]
LLAMA_INDEX_DEFAULT_ALL_SUPPORTED_FORMATS_LIST = [".txt", ".docx", ".hwp", ".ipynb", ".csv", ".jpeg", ".jpg", ".mbox", ".md", ".mp3", ".mp4", ".pdf", ".png", ".ppt", ".pptx", ".pptm"]

# PROMPT
FORM_PROMPT_GROUP_SAMPLE = json.dumps(
    [{"name": "Default", "data": PROPERTY_PROMPT_UNIT_DEFAULT_VALUE}],
    indent=INDENT_SIZE,
)

SENTENCE_PROMPT_GROUP_SAMPLE = """[
    {
        "name": "alex_brogan",
        "data": [
            {
                "name": "sample_1",
                "content": "Identify the 20% of [topic or skill] that will yield 80% of the desired results and provide a focused learning plan to master it."
            },
            {
                "name": "sample_2",
                "content": "Explain [topic or skill] in the simplest terms possible as if teaching it to a complete beginner. Identify gaps in my understanding and suggest resources to fill them."
            }
        ]
    },
    {
        "name": "awesome_chatGPT_prompts",
        "data": [
            {
                "name": "linux_terminal",
                "content": "I want you to act as a linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. do not write explanations. do not type commands unless I instruct you to do so. when i need to tell you something in english, i will do so by putting text inside curly brackets {like this}. my first command is pwd"
            },
            {
                "name": "english_translator_and_improver",
                "content": "I want you to act as an English translator, spelling corrector and improver. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in English. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, upper level English words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations. My first sentence is \"istanbulu cok seviyom burada olmak cok guzel\""
            },
        ]
    }
]"""

## Data for random prompt generating feature for image generation
hair_color_randomizer = [
    "blonde hair",
    "red hair",
    "blue hair",
    "dark hair",
    "green hair",
    "white hair",
]
hair_style_randomizer = [
    "Long straight hair",
    "Short pixie cut",
    "Bob haircut",
    "Layered haircut",
    "Curly hair",
    "Wavy hair",
    "Ponytail",
    "Messy bun",
    "French braid",
    "Dutch braid",
    "Fishtail braid",
    "High bun",
    "Low bun",
    "Top knot",
    "Half-up half-down hairstyle",
    "Braided crown",
    "Side-swept bangs",
    "Bangs/fringe",
    "Chignon",
    "Waterfall braid",
    "Mohawk",
    "Beach waves",
    "Updo",
    "French twist",
    "Cornrows",
    "Dreadlocks",
    "Pigtails",
    "Space buns",
    "Sock bun",
]
clothes_randomizer = [
    "wearing denim jacket",
    "wearing coat",
    "wearing blazer",
    "wearing blouse",
    "wearing biker clothes",
    "wearing distressed jeans",
    "wearing hoodie",
]
expression_randomizer = [
    "Smile",
    "Grin",
    "Closed eyes",
    "Squinting",
    "(laughing:1.2)",
    "(giggle:1.2)",
    "(Angry face:1.4)",
    "Frowning face",
    "Confused face",
    "Boredom",
    "Eyebrow furrow",
    "Eye roll",
    "Smirk",
]
pose_randomizer = ["sitting", "lying", "leaning", "cross-legged"]
camera_distance_randomizer = [
    "(extreme close-up:1.5)",
    "(medium full shot:1.5)",
    "(close-up:1.5)",
    "(establishing shot:1.5)",
    "(medium close-up:1.5)",
    "(point-of-view:1.5)",
    "(medium shot:1.5)",
    "(cowboy shot:1.5)",
    "(long shot:1.5)",
    "(upper body:1.5)",
    "(full shot:1.5)",
    "(full body:1.5)",
]
camera_angle_randomizer = [
    "(front view:1.5)",
    "(from below:1.5)",
    "(bilaterally symmetrical:1.5)",
    "(from behind:1.5)",
    "(side view:1.5)",
    "(wide angle view:1.5)",
    "(back view:1.5)",
    "(fisheyes view:1.5)",
    "(from above:1.5)",
    "(macro view:1.5)",
    "(overhead shot:1.5)",
    "(straight on:1.5)",
    "(top down view:1.5)",
    "(hero view:1.5)",
    "(bird's eye view:1.5)",
    "(low view:1.5)",
    "(high angle:1.5)",
    "(worm's eye view:1.5)",
    "(slightly above:1.5)",
    "(selfie:1.5)",
]

adding_lighting_randomizer = [
    "bloom",
    "backlight",
    "sun light",
    "soft lighting",
    "god rays",
    "studio light",
    "hard lighting",
    "volumetic lighting",
    "bioluminescent light",
]
wind_randomizer = ["(wind:0)", "(wind:0.5)", "(wind:1)", "(wind:1.5)", "(wind:2)"]
acc1_randomizer = ["wearing sunglasses", "tattoo"]
acc3_randomizer = ["wearing beanie", "wearing beret", "wearing cap", "wearing fedora"]
attr2_randomizer = ["put on earphones", "piercing on nose", "put on headphones"]
location_randomizer = [
    "In the office",
    "Tokyo street",
    "In the living room",
    "In the music studio",
    "On the beach",
    "In the club",
]

RANDOMIZING_PROMPT_SOURCE_ARR = [
    hair_color_randomizer,
    hair_style_randomizer,
    clothes_randomizer,
    expression_randomizer,
    pose_randomizer,
    camera_distance_randomizer,
    camera_angle_randomizer,
    adding_lighting_randomizer,
    wind_randomizer,
    acc1_randomizer,
]

# DEFAULT Configuration data for the application settings
# Initialize here to avoid circular import
# ----------------------------
CONFIG_DATA = {
    "General": {
        # Language
        "lang": "English",
        # DB
        "db": "conv",
        # GUI & Application settings
        "TAB_IDX": 0,
        "show_chat_list": True,
        "show_setting": True,
        "do_not_ask_again": False,
        "show_prompt": True,
        "notify_finish": True,
        "show_secondary_toolbar": True,
        "focus_mode": False,
        "show_as_markdown": True,
        "show_realtime_api": False,
        "run_at_startup": True,
        "manual_update": True,
        # Columns
        "chat_column_to_show": ["id", "name", "insert_dt", "update_dt"],
        "image_column_to_show": [
            "id",
            "model",
            "width",
            "height",
            "provider",
            "prompt",
            "negative_prompt",
            "n",
            "quality",
            "data",
            "style",
            "revised_prompt",
            "update_dt",
            "insert_dt",
        ],
        # Parameters
        "model": DEFAULT_LLM,
        "system": "You are a helpful assistant.",
        "stream": True,
        "temperature": 1,
        "max_tokens": -1,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "json_object": False,
        "maximum_messages_in_parameter": MAXIMUM_MESSAGES_IN_PARAMETER,
        "use_max_tokens": False,
        # Llama Index
        "use_llama_index": False,
        "llama_index_directory": "",
        "llama_index_supported_formats": LLAMA_INDEX_DEFAULT_SUPPORTED_FORMATS_LIST,
        # Customize
        "background_image": "",
        "user_image": DEFAULT_USER_IMAGE_PATH,
        "ai_image": DEFAULT_AI_IMAGE_PATH,
        "font_size": DEFAULT_FONT_SIZE,
        "font_family": DEFAULT_FONT_FAMILY,
        "apply_user_defined_styles": False,
        # G4F
        "g4f_model": DEFAULT_LLM,
        "provider": G4F_PROVIDER_DEFAULT,
        "g4f_use_chat_history": G4F_USE_CHAT_HISTORY,
        # STT and TTS settings
        "voice_provider": TTS_DEFAULT_PROVIDER,
        "voice": TTS_DEFAULT_VOICE,
        "voice_speed": TTS_DEFAULT_SPEED,
        "auto_play_voice": TTS_DEFAULT_AUTO_PLAY,
        "auto_stop_silence_duration": TTS_DEFAULT_AUTO_STOP_SILENCE_DURATION,
    },
    "IMAGE": {
        "model": G4F_DEFAULT_IMAGE_MODEL,
        "width": 1024,
        "height": 1024,
        "show_history": True,
        "show_setting": True,
        "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
        "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
        "directory": QFILEDIALOG_DEFAULT_DIRECTORY,
        "is_save": True,
        "continue_generation": False,
        "number_of_images_to_create": 2,
        "save_prompt_as_text": True
    }

    # "DALLE": {
    #     "quality": "standard",
    #     "n": 1,
    #     "size": "1024x1024",
    #     "style": "vivid",
    #     "response_format": "b64_json",
    #     "width": 1024,
    #     "height": 1024,
    #     "prompt_type": 1,
    #     "show_history": True,
    #     "show_setting": True,
    #     "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
    #     "directory": QFILEDIALOG_DEFAULT_DIRECTORY,
    #     "is_save": True,
    #     "continue_generation": False,
    #     "number_of_images_to_create": 2,
    #     "save_prompt_as_text": True,
    #     "show_prompt_on_image": False,
    # },
    # "REPLICATE": {
    #     "model": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    #     "width": 768,
    #     "height": 768,
    #     "show_history": True,
    #     "show_setting": True,
    #     "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
    #     "directory": QFILEDIALOG_DEFAULT_DIRECTORY,
    #     "is_save": True,
    #     "continue_generation": False,
    #     "number_of_images_to_create": 2,
    #     "save_prompt_as_text": True,
    #     "show_prompt_on_image": False,
    #     "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
    # },
    # "G4F_IMAGE": {
    #     "model": G4F_DEFAULT_IMAGE_MODEL,
    #     "provider": G4F_PROVIDER_DEFAULT,
    #     "show_history": True,
    #     "show_setting": True,
    #     "prompt": "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
    #     "directory": QFILEDIALOG_DEFAULT_DIRECTORY,
    #     "is_save": True,
    #     "continue_generation": False,
    #     "number_of_images_to_create": 2,
    #     "save_prompt_as_text": True,
    #     "show_prompt_on_image": False,
    #     "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
    # },
}


# Dynamically add the API keys to the configuration data
def update_general_config_with_api_keys(config_data, api_configs):
    for config in api_configs:
        config_data["General"][config["env_var_name"]] = config["api_key"]


update_general_config_with_api_keys(CONFIG_DATA, DEFAULT_API_CONFIGS)

# Set the default llama index cache directory for preventing any issues such as PermissionError
os.environ["NLTK_DATA"] = os.path.join(get_config_directory(), "llama_index_cache")

# Update the __all__ list with the PEP8 standard dunder names
__all__ = ["__version__", "__author__"]

# Update the __all__ list with the constants
__all__.extend([name for name, value in globals().items() if name.isupper()])
