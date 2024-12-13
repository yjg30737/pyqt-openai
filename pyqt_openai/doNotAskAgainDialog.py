from __future__ import annotations

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import getSeparator


class DoNotAskAgainDialog(QDialog):
    doNotAskAgainChanged = Signal(bool)

    def __init__(
        self,
        do_not_ask_again: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        do_not_ask_again_message: str = LangClass.TRANSLATIONS[
            "Would you like to exit the application? If you won't, it will be running in the background."
        ]
        do_not_ask_again_checkbox_message = LangClass.TRANSLATIONS["Do not ask again"]
        self.__initVal(
            do_not_ask_again,
            do_not_ask_again_message,
            do_not_ask_again_checkbox_message,
        )
        self.__initUi()

    def __initVal(
        self,
        do_not_ask_again,
        do_not_ask_again_message,
        do_not_ask_again_checkbox_message,
    ):
        self.__is_cancel = False
        self.__do_not_ask_again = do_not_ask_again
        self.__do_not_ask_again_message = do_not_ask_again_message
        self.__do_not_ask_again_checkbox_message = do_not_ask_again_checkbox_message

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Exit"])
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.label: QLabel = QLabel(self.__do_not_ask_again_message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.yesButton: QPushButton = QPushButton(LangClass.TRANSLATIONS["Yes"])
        self.yesButton.clicked.connect(self.accept)

        self.noButton: QPushButton = QPushButton(LangClass.TRANSLATIONS["No"])
        self.noButton.clicked.connect(self.reject)

        self.cancelButton: QPushButton = QPushButton(LangClass.TRANSLATIONS["Cancel"])
        self.cancelButton.clicked.connect(self.__cancel)

        self.doNotAskAgainCheckBox: QCheckBox = QCheckBox(
            self.__do_not_ask_again_checkbox_message,
        )
        self.doNotAskAgainCheckBox.setChecked(self.__do_not_ask_again)
        self.doNotAskAgainCheckBox.stateChanged.connect(self.__onCheckBoxStateChanged)

        sep = getSeparator("horizontal")

        lay = QHBoxLayout()
        lay.addWidget(self.doNotAskAgainCheckBox)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.yesButton)
        lay.addWidget(self.noButton)
        lay.addWidget(self.cancelButton)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)
        btnWidget = QWidget()
        btnWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.label)
        lay.addWidget(sep)
        lay.addWidget(btnWidget)

        self.setLayout(lay)

    def __cancel(self):
        self.__is_cancel = True
        self.reject()

    def __onCheckBoxStateChanged(
        self,
        state: int,
    ) -> None:
        self.__do_not_ask_again: bool = state == 2
        self.doNotAskAgainChanged.emit(self.__do_not_ask_again)

    def isCancel(self):
        return self.__is_cancel
