"""This is the file that contains the global variables that are used, or possibly used, throughout the application."""
from __future__ import annotations

from g4f.client import Client
from openai import OpenAI

from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamaindex import LlamaIndexWrapper
from pyqt_openai.util.replicate import ReplicateWrapper

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = LlamaIndexWrapper()

G4F_CLIENT = Client()

# For Image Generation and TTS & STT
OPENAI_CLIENT = OpenAI(api_key="")

# For Image Generation
REPLICATE_CLIENT = ReplicateWrapper(api_key="")
