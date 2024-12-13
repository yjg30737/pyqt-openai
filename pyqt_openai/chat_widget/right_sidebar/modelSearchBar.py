from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCompleter, QLineEdit

from pyqt_openai.util.common import get_chat_model


class ModelSearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        all_models = get_chat_model()
        # TODO LANGAUGE
        self.setPlaceholderText("Start typing a model name...")

        completer = QCompleter(all_models)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(completer)
