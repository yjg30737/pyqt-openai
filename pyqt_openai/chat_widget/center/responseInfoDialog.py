from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QFormLayout, QLabel, QPushButton

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import getSeparator

if TYPE_CHECKING:
    from pyqt_openai.models import ChatMessageContainer


class ResponseInfoDialog(QDialog):
    def __init__(self, result_info: ChatMessageContainer, parent=None):
        super().__init__(parent)
        self.__initVal(result_info)
        self.__initUi()

    def __initVal(self, result_info):
        self.__result_info = result_info

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Message Result"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        lbls = []
        for k, v in self.__result_info.get_items(excludes=["content"]):
            if k == "favorite":
                lbls.append(QLabel(f'{k}: {"Yes" if v else "No"}'))
            else:
                lbls.append(QLabel(f"{k}: {v}"))

        sep = getSeparator("horizontal")

        okBtn = QPushButton("OK")
        okBtn.clicked.connect(self.accept)

        lay = QFormLayout()
        for lbl in lbls:
            lay.addWidget(lbl)
        lay.addWidget(sep)
        lay.addWidget(okBtn)

        self.setLayout(lay)
