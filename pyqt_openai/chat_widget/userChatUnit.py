import pyperclip
from pyqt_openai.svgButton import SvgButton
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout, QLabel


class UserChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__plain_text = ''
        self.__find_f = False

    def __initUi(self):
        # common
        menuWidget = QWidget()
        lay = QHBoxLayout()

        self.__icon = QLabel()
        self.__icon.setFixedSize(24, 24)

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        copyBtn = SvgButton()
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self.__icon)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(copyBtn)
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

    def toPlainText(self):
        return self.__plain_text