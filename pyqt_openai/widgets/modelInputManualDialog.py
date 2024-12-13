from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QDialog, QHBoxLayout, QLabel

from pyqt_openai import DEFAULT_WARNING_COLOR, SMALL_LABEL_PARAM

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class ModelInputManualDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__warningMessage = (
            "💡 <b>Tip:</b> For models other than OpenAI and Anthropic, enter the model name as "
            "<code>[ProviderName]/[ModelName]</code>.<br><br>"
            "🔗 For details on <b>ProviderName</b> and <b>ModelName</b>, check out the "
            "<a href='https://docs.litellm.ai/docs/providers'>LiteLLM documentation</a>! 😊<br><br>"
            "⚠️ <b>Note:</b> Some models may not support <b>JSON Mode</b> or <b>LlamaIndex</b> features."
        )

    def __initUi(self):
        self.setWindowTitle("Model Input Manual")
        self.__warningLbl: QLabel = QLabel()
        self.__warningLbl.setStyleSheet(
            f"color: {DEFAULT_WARNING_COLOR};",
        )  # Text color remains orange for visibility.
        self.__warningLbl.setWordWrap(True)
        self.__warningLbl.setFont(QFont(*SMALL_LABEL_PARAM))
        self.__warningLbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.__warningLbl.setOpenExternalLinks(True)  # Enable hyperlink functionality.
        self.__warningLbl.setText(self.__warningMessage)  # Ensure HTML is passed as text.

        lay = QHBoxLayout()
        lay.addWidget(self.__warningLbl)
        self.setLayout(lay)
