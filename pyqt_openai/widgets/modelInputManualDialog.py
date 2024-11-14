from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QTableWidget

from pyqt_openai import SMALL_LABEL_PARAM
from pyqt_openai.util.common import get_litellm_prefixes


class ModelInputManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__warningMessage = (
            "💡 <b>Tip</b> For models other than OpenAI and Anthropic, enter the model name as `[ProviderName]/[ModelName]`.\n\n"
            "🔗 For details on `ProviderName` and `ModelName`, check out the "
            "<a href='https://docs.litellm.ai/docs/providers'>LiteLLM documentation</a>! 😊\n\n"
            "⚠️ Note: Some models may not support <b>JSON Mode</b> or <b>LlamaIndex</b> features."
        )

    def __initUi(self):
        self.__warningLbl = QLabel()
        self.__warningLbl.setStyleSheet("color: orange;")
        self.__warningLbl.setOpenExternalLinks(True)
        self.__warningLbl.setFont(QFont(SMALL_LABEL_PARAM))
        self.__warningLbl.setText(self.__warningMessage)
        self.__warningLbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        # prefixTable = QTableWidget()
        # prefixes = get_litellm_prefixes()
        # prefixTable.setColumnCount(len(list(prefixes[0].keys())))
        # prefixTable.setHorizontalHeaderLabels(list(prefixes[0].keys()))
        # for prefix in prefixes:
        #     prefixTable.insertRow(prefixTable.rowCount())
        #     prefixTable.setItem(prefixTable.rowCount() - 1, 0, QLabel(prefix))

        lay = QHBoxLayout()
        lay.addWidget(self.__warningLbl)
        # lay.addWidget(prefixTable)
        self.setLayout(lay)
