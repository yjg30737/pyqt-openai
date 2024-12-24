from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import getSeparator


class InputDialog(QDialog):
    def __init__(
        self,
        title: str,
        text: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initUi(title, text)

    def __initUi(
        self,
        title: str,
        text: str,
    ):
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__newName: QLineEdit = QLineEdit(text)
        self.__newName.textChanged.connect(self.__setAccept)
        sep: QWidget = getSeparator("horizontal")

        self.__okBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["OK"])
        self.__okBtn.clicked.connect(self.accept)

        cancelBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["Cancel"])
        cancelBtn.clicked.connect(self.close)

        lay: QHBoxLayout = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget: QWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay: QVBoxLayout = QVBoxLayout()
        lay.addWidget(self.__newName)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

    def getText(self):
        return self.__newName.text()

    def __setAccept(
        self,
        text: str,
    ):
        self.__okBtn.setEnabled(text.strip() != "")
