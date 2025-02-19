from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCompleter, QLineEdit

from pyqt_openai.util.common import get_chat_model


class ModelSearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO LANGAUGE
        self.setPlaceholderText("Start typing a model name...")
        self.setChatModel()

        self.textChanged.connect(self.onTextChanged)

    def setChatModel(self, all_models=None):
        if all_models is None:
            all_models = get_chat_model()
        completer = QCompleter(all_models)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(completer)
        if all_models is not None and isinstance(all_models, list) and len(all_models) > 0:
            # Show the first model in the list
            self.setText(all_models[0])

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.completer():
            self.completer().complete()

    def onTextChanged(self, text):
        if not text:
            self.completer().setCompletionPrefix("")
            self.completer().complete()