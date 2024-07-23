import json
import os.path

from qtpy.QtCore import QLocale

from pyqt_openai.constants import DEFAULT_LANGUAGE, LANGUAGE_FILE, LANGUAGE_DICT


class WordsDict(dict):
    """
    Only used for release version
    to prevent KeyError
    """
    def __missing__(self, key):
        return key


class LangClass:
    """
    LangClass is the class that manages the language of the application.
    It reads the language file and sets the language.
    """
    TRANSLATIONS = WordsDict()

    @classmethod
    def lang_changed(cls, lang=None):
        with open(os.path.join(os.path.dirname(__file__), LANGUAGE_FILE), 'r', encoding='utf-8') as file:
            translations_data = json.load(file)

        if not lang:
            language = QLocale.system().name()
            if language not in translations_data:
                language = DEFAULT_LANGUAGE  # Default language
        else:
            language = LANGUAGE_DICT[lang]

        cls.TRANSLATIONS = WordsDict(translations_data[language])

        for k, v in LANGUAGE_DICT.items():
            if v == language:
                return k