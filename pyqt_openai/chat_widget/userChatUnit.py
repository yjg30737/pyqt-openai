import re

import pyperclip
from qtpy.QtGui import QColor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from pyqt_openai.svgButton import SvgButton


class UserChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__plain_text = ''

    def __initUi(self):
        # common
        menuWidget = QWidget()
        lay = QHBoxLayout()

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        copyBtn = SvgButton()
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(copyBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setStyleSheet('QWidget { background-color: #BBB }')

        self.__lbl = QLabel()
        self.__lbl.setStyleSheet('QLabel { padding: 6px }')

        self.__lbl.setAlignment(Qt.AlignLeft)
        self.__lbl.setWordWrap(True)
        self.__lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.__lbl.setOpenExternalLinks(True)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__lbl)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

    def __copy(self):
        pyperclip.copy(self.text())

    def setText(self, text):
        self.__lbl.setText(text)

    def text(self):
        return self.__lbl.text()

    def removeFormat(self):
        self.setText(self.__plain_text)

    def highlightWord(self, text, color_str):
        self.__plain_text = self.text()

        color = QColor(color_str)
        print(f'highlight {text} with {color.name()}')

        m = re.finditer(text, self.__plain_text)
        formatted_text = ''
        last_end = 0

        for _ in m:
            start, end = _.span()

            formatted_text += self.__plain_text[last_end:start]

            formatted_text += "<span style='color:red'>" + self.__plain_text[start:end] + "</span>"

            last_end = end

        formatted_text += self.__plain_text[last_end:]

        self.__lbl.setText(formatted_text)
        # self.setText(formatted_text, True)