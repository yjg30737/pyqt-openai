"""
This is the file that contains the global variables that are used, or possibly used, throughout the application.
"""

from g4f.client import Client
from openai import OpenAI

from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamapage_script import GPTLLamaIndexWrapper
from pyqt_openai.util.replicate_script import ReplicateWrapper

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = GPTLLamaIndexWrapper()

G4F_CLIENT = Client()

# For Whisper
OPENAI_CLIENT = OpenAI(api_key="")

REPLICATE_CLIENT = ReplicateWrapper(api_key="")
