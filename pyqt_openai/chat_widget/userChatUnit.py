import pyperclip
from qtpy.QtCore import Qt
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QTextBrowser, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout

from pyqt_openai import DEFAULT_ICON_SIZE, ICON_COPY, MESSAGE_MAXIMUM_HEIGHT, MESSAGE_ADDITIONAL_HEIGHT
from pyqt_openai.chat_widget.messageTextBrowser import MessageTextBrowser
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.circleProfileImage import RoundedImage


class UserChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__plain_text = ''
        self.__find_f = False

    def __initUi(self):
        menuWidget = QWidget()
        lay = QHBoxLayout()

        self.__icon = RoundedImage()
        self.__icon.setMaximumSize(*DEFAULT_ICON_SIZE)

        copyBtn = Button()
        copyBtn.setStyleAndIcon(ICON_COPY)
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self.__icon)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(copyBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())

        self.__lbl = MessageTextBrowser()

        self.__lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.__lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.__lbl.setOpenExternalLinks(True)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__lbl)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.setBackgroundRole(QPalette.ColorRole.Base)
        self.setAutoFillBackground(True)

        self.__lbl.adjustBrowserHeight()

    def __copy(self):
        pyperclip.copy(self.text())

    def setText(self, text):
        self.__lbl.setText(text)
        self.__lbl.adjustBrowserHeight()

    def text(self):
        return self.__lbl.toPlainText()

    def toPlainText(self):
        return self.__plain_text

    def getIcon(self):
        return self.__icon.getImage()

    def setIcon(self, filename):
        self.__icon.setImage(filename)