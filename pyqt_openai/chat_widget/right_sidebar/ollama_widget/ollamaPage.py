from __future__ import annotations

import threading

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QComboBox,
    QFormLayout,
    QSizePolicy,
    QTextBrowser,
    QWidget,
    QLabel,
    QDialog,
)

from pyqt_openai.chat_widget.right_sidebar.ollama_widget.ollamaModelsManagerDialog import OllamaModelManagerDialog
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.globals import OLLAMA_CLIENT
from pyqt_openai.util.common import (
    getSeparator,
    get_ollama_model,
)
from pyqt_openai.widgets.featureButton import FeatureButton


class OllamaPage(QWidget):
    onToggleJSON = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__model = 'llama3.1:8b'

    def __initUi(self):
        manualBrowser = QTextBrowser()
        manualBrowser.setOpenExternalLinks(True)
        manualBrowser.setOpenLinks(True)

        warning_lbl = QLabel()
        warning_lbl.setWordWrap(True)

        is_ollama_installed = OLLAMA_CLIENT.is_ollama_installed()

        if is_ollama_installed:
            warning_lbl.setText(
                "Ollama is installed. You can run models locally using Ollama.",
            )
            warning_lbl.setStyleSheet("color: green; font-weight: bold;")
            ollama_thread = threading.Thread(target=OLLAMA_CLIENT.run_ollama_serve())
            ollama_thread.start()
        else:
            warning_lbl.setText("Ollama is not installed. Please install Ollama to use this feature.")
            warning_lbl.setStyleSheet("color: red; font-weight: bold;")

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
        if is_ollama_installed:
            llama_models = get_ollama_model(name_only=True)
            self.__modelCmbBox.addItems(llama_models)
            self.__modelCmbBox.setCurrentText(self.__model)
        self.__modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        ollamaButton = FeatureButton()
        ollamaButton.clicked.connect(self.__showOllamaModelsDialog)
        ollamaButton.updateStylesheet('#007BFF')
        ollamaButton.setText('Manage Models')

        lay = QFormLayout()
        lay.addRow(warning_lbl)
        lay.addRow(manualBrowser)
        lay.addRow(getSeparator("horizontal"))
        lay.addRow("Model", self.__modelCmbBox)
        lay.addRow(ollamaButton)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

        ollamaButton.setEnabled(is_ollama_installed)

    def __modelChanged(self, v):
        self.__model = v
        CONFIG_MANAGER.set_general_property("ollama_model", v)

    def __showOllamaModelsDialog(self):
        dialog = OllamaModelManagerDialog(self)
        # If the dialog is closed, update the model list
        if dialog.exec() == QDialog.Accepted:
            # Refresh the model list in the combo box
            self.__modelCmbBox.clear()
            llama_models = get_ollama_model(name_only=True)
            self.__modelCmbBox.addItems(llama_models)
            # Set the current model to the first one in the list
            if llama_models:
                self.__modelCmbBox.setCurrentText(llama_models[0])