from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import getSeparator, is_prompt_group_name_valid


class PromptGroupDirectInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["New Prompt"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__name = QLineEdit()
        self.__name.setPlaceholderText(LangClass.TRANSLATIONS["Name"])
        self.__name.textChanged.connect(
            lambda x: self.__okBtn.setEnabled(x.strip() != ""),
        )

        sep = getSeparator("horizontal")

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS["OK"])
        self.__okBtn.clicked.connect(self.__accept)

        cancelBtn = QPushButton(LangClass.TRANSLATIONS["Cancel"])
        cancelBtn.clicked.connect(self.close)

        hlay = QHBoxLayout()
        hlay.addWidget(self.__okBtn)
        hlay.addWidget(cancelBtn)
        hlay.setAlignment(Qt.AlignmentFlag.AlignRight)
        hlay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(hlay)

        vlay = QVBoxLayout()
        vlay.addWidget(self.__name)
        vlay.addWidget(sep)
        vlay.addWidget(okCancelWidget)

        self.setLayout(vlay)

    def getPromptGroupName(self) -> str:
        return self.__name.text()

    def __accept(self):
        f = is_prompt_group_name_valid(self.__name.text())
        if f:
            self.accept()
        else:
            self.__name.setFocus()
            QMessageBox.warning(  # type: ignore[call-arg]
                self,
                LangClass.TRANSLATIONS["Warning"],
                LangClass.TRANSLATIONS["Prompt name already exists."],
            )
            return
