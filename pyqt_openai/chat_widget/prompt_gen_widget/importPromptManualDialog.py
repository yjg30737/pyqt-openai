from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from pyqt_openai import (
    AWESOME_CHATGPT_PROMPTS_URL,
    SENTENCE_PROMPT_GROUP_SAMPLE,
)
from pyqt_openai.chat_widget.prompt_gen_widget.promptCsvRightFormSampleDialog import (
    PromptCSVRightFormSampleDialog,
)
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import showJsonSample
from pyqt_openai.widgets.jsonEditor import JSONEditor


class ImportPromptManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Import Manual"])
        self.__jsonSampleWidget = JSONEditor()
        jsonRightFormBtn = QPushButton(
            LangClass.TRANSLATIONS[
                "What is the right form of json to be imported?"
            ],
        )

        csvRightFormBtn = QPushButton(
            LangClass.TRANSLATIONS[
                "What is the right form of csv to be imported?"
            ],
        )

        jsonRightFormBtn.clicked.connect(self.__showJsonSample)
        csvRightFormBtn.clicked.connect(self.__showCSVSample)

        awesomeChatGptPromptDownloadLink = QLabel(f'Try downloading <a href="{AWESOME_CHATGPT_PROMPTS_URL}">Awesome ChatGPT prompts</a> and import! 😊')
        awesomeChatGptPromptDownloadLink.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction,
        )
        awesomeChatGptPromptDownloadLink.setOpenExternalLinks(True)  # Enable hyperlink functionality.

        lay = QVBoxLayout()
        lay.addWidget(jsonRightFormBtn)
        lay.addWidget(csvRightFormBtn)
        lay.addWidget(awesomeChatGptPromptDownloadLink)
        self.setLayout(lay)

    def __showJsonSample(self):
        showJsonSample(self.__jsonSampleWidget, SENTENCE_PROMPT_GROUP_SAMPLE)

    def __showCSVSample(self):
        dialog = PromptCSVRightFormSampleDialog(self)
        dialog.exec()
