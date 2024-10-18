import pyperclip
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)

from pyqt_openai import DEFAULT_ICON_SIZE, ICON_COPY
from pyqt_openai.chat_widget.center.messageTextBrowser import MessageTextBrowser
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.circleProfileImage import RoundedImage


class ChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self._menuWidget = QWidget()
        lay = QHBoxLayout()

        self._icon = RoundedImage()
        self._icon.setMaximumSize(*DEFAULT_ICON_SIZE)

        self._copyBtn = Button()
        self._copyBtn.setStyleAndIcon(ICON_COPY)
        self._copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self._icon)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self._copyBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        self._menuWidget.setLayout(lay)
        self._menuWidget.setMaximumHeight(self._menuWidget.sizeHint().height())

        self._lbl = MessageTextBrowser()
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)

        lay = QVBoxLayout()
        lay.addWidget(self._menuWidget)
        lay.addWidget(self._lbl)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.setBackgroundRole(QPalette.ColorRole.Base)
        self.setAutoFillBackground(True)

        self._lbl.adjustBrowserHeight()

    def __copy(self):
        pyperclip.copy(self.getText())

    def setText(self, text: str):
        self._lbl.setText(text)
        self._lbl.adjustBrowserHeight()

    def getText(self):
        return self._lbl.toPlainText()

    def getIcon(self):
        return self._icon.getImage()

    def setIcon(self, filename):
        self._icon.setImage(filename)

    def getLbl(self):
        return self._lbl

    def getMenuWidget(self):
        return self._menuWidget
