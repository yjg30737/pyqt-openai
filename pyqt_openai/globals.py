"""
This is the file that contains the global variables that are used, or possibly used, throughout the application.
"""

import anthropic
import google.generativeai as genai
from openai import OpenAI
from g4f.client import Client

from pyqt_openai import DEFAULT_GEMINI_MODEL
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.util.llamapage_script import GPTLLamaIndexWrapper
from pyqt_openai.util.replicate_script import ReplicateWrapper

DB = SqliteDatabase()

LLAMAINDEX_WRAPPER = GPTLLamaIndexWrapper()

G4F_CLIENT = Client()

OPENAI_CLIENT = OpenAI(api_key="")
GEMINI_CLIENT = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
ANTHROPIC_CLIENT = anthropic.Anthropic(api_key="")

REPLICATE_CLIENT = ReplicateWrapper(api_key="")
