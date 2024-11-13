from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QCompleter

from pyqt_openai.util.script import get_chat_model


class ModelSearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        all_models = get_chat_model()
        # TODO LANGAUGE
        self.setPlaceholderText("Start typing a model name...")

        completer = QCompleter(all_models)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(completer)