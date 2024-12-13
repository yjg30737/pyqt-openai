from __future__ import annotations

import json

from qtpy.QtCore import QLocale

from pyqt_openai import DEFAULT_LANGUAGE, LANGUAGE_DICT, LANGUAGE_FILE


class WordsDict(dict):
    """Only used for release version
    to prevent KeyError.
    """

    def __missing__(self, key):
        return key


class LangClass:
    """LangClass is the class that manages the language of the application.
    It reads the language file and sets the language.
    """

    TRANSLATIONS = WordsDict()

    @classmethod
    def lang_changed(cls, lang=None):
        with open(LANGUAGE_FILE, encoding="utf-8") as file:
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
