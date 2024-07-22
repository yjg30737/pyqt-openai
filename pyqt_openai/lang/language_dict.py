import json
import os.path

from qtpy.QtCore import QLocale

from pyqt_openai.constants import DEFAULT_LANGUAGE, LANGUAGE_FILE


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
        "Japanese": "ja_JP",
        "Bengali": "bn_IN",
        "Urdu": "ur_PK",
        "Indonesian": "id_ID",
        "Portuguese": "pt_BR"
    }

    @classmethod
    def lang_changed(cls, lang=None):
        with open(os.path.join(os.path.dirname(__file__), LANGUAGE_FILE), 'r', encoding='utf-8') as file:
            translations_data = json.load(file)

        if not lang:
            language = QLocale.system().name()
            if language not in translations_data:
                language = DEFAULT_LANGUAGE  # Default language
        else:
            language = cls.LANGUAGE_DICT[lang]

        cls.TRANSLATIONS = translations_data[language]

        for k, v in cls.LANGUAGE_DICT.items():
            if v == language:
                return k