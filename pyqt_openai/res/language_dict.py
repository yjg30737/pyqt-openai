import json
import os.path

from qtpy.QtCore import QLocale


class LangClass:
    TRANSLATIONS = {}
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
        "Japanese": "ja_JP"
    }

    @classmethod
    def lang_changed(cls, lang=None):

        with open(os.path.join(os.path.dirname(__file__), 'translations.json'), 'r', encoding='utf-8') as file:
            translations_data = json.load(file)

        if not lang:
            language = QLocale.system().name()
            if language not in translations_data:
                language = 'en_US'  # Default language
        else:
            language = cls.LANGUAGE_DICT[lang]

        cls.TRANSLATIONS = translations_data[language]

        for k, v in cls.LANGUAGE_DICT.items():
            if v == language:
                return k