from __future__ import annotations

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QSizePolicy,
    QTextBrowser,
    QWidget,
)

from pyqt_openai import G4F_PROVIDER_DEFAULT
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import (
    getSeparator,
    get_g4f_models,
    get_g4f_models_by_provider,
    get_ollama_model,
)
from pyqt_openai.widgets.ollamaModelButton import OllamaButton


class OllamaPage(QWidget):
    onToggleJSON = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__stream = CONFIG_MANAGER.get_general_property("stream")
        self.__model = 'llama3.1:8b'

    def __initUi(self):
        manualBrowser = QTextBrowser()
        manualBrowser.setOpenExternalLinks(True)
        manualBrowser.setOpenLinks(True)

        # TODO LANGUAGE
        manualBrowser.setHtml(
            """
        <h2>Using Ollama (Free)</h2>
        <h3>Description</h3>
        <p>- Ollama is a free and open-source tool for running large language models locally.</p>
        <p>- You need to install Ollama on your system.</p>
        """,
        )
        manualBrowser.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred,
        )

        self.__modelCmbBox = QComboBox()
        self.__modelCmbBox.addItems(get_ollama_model(name_only=True))
        self.__modelCmbBox.setCurrentText(self.__model)
        self.__modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        ollamaButton = OllamaButton()
        ollamaButton.clicked.connect(self.__showOllamaModelsDialog)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText(LangClass.TRANSLATIONS["Stream"])

        g4f_use_chat_historyChkBox = QCheckBox("Use chat history")
        g4f_use_chat_historyChkBox.setChecked(
            CONFIG_MANAGER.get_general_property("g4f_use_chat_history"),
        )
        g4f_use_chat_historyChkBox.toggled.connect(self.__saveChatHistory)

        lay = QFormLayout()
        lay.addRow(manualBrowser)
        lay.addRow(getSeparator("horizontal"))
        lay.addRow("Model", self.__modelCmbBox)
        lay.addRow(ollamaButton)
        lay.addRow(streamChkBox)
        lay.addRow(g4f_use_chat_historyChkBox)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

    def __modelChanged(self, v):
        self.__model = v
        CONFIG_MANAGER.set_general_property("g4f_model", v)

    def __streamChecked(self, f):
        self.__stream = f
        CONFIG_MANAGER.set_general_property("stream", f)

    def __saveChatHistory(self, f):
        CONFIG_MANAGER.set_general_property("g4f_use_chat_history", f)

    def __showOllamaModelsDialog(self):
        print('Show Ollama Models Dialog')
