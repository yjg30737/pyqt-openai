import pyperclip
from qtpy.QtGui import QPalette
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTextBrowser, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout, QLabel

from pyqt_openai import DEFAULT_ICON_SIZE, ICON_COPY, MESSAGE_MAXIMUM_HEIGHT, MESSAGE_ADDITIONAL_HEIGHT
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

        self.__lbl = QTextBrowser()
        self.__lbl.setStyleSheet('QTextBrowser { padding: 6px }')

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

        self.adjustBrowserHeight()

    def adjustBrowserHeight(self):
        document_height = self.__lbl.document().size().height() + MESSAGE_ADDITIONAL_HEIGHT
        max_height = MESSAGE_MAXIMUM_HEIGHT

        if document_height < max_height:
            self.__lbl.setMinimumHeight(int(document_height))
        else:
            self.__lbl.setMinimumHeight(int(max_height))

    def __copy(self):
        pyperclip.copy(self.text())

    def setText(self, text):
        self.__lbl.setText(text)

    def text(self):
        return self.__lbl.toPlainText()

    def toPlainText(self):
        return self.__plain_text

    def getIcon(self):
        return self.__icon.getImage()

    def setIcon(self, filename):
        self.__icon.setImage(filename)