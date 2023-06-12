import pyperclip

from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication, QHBoxLayout
from PyQt5.QtCore import Qt

from pyqt_openai.svgButton import SvgButton


class ChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        copyBtn = SvgButton(self)
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay = QHBoxLayout()
        lay.addWidget(copyBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setStyleSheet('QWidget { background-color: #BBB }')

        self.__lbl = QLabel()
        self.__lbl.setStyleSheet('QLabel { padding: 1rem }')

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__lbl)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def __copy(self):
        pyperclip.copy(self.__lbl.text())

    def getLabel(self) -> QLabel:
        return self.__lbl

    def text(self):
        return self.__lbl.text()

    def alignment(self):
        return self.__lbl.alignment()

    def setAlignment(self, a0):
        self.__lbl.setAlignment(a0)

    def setText(self, text: str):
        return self.__lbl.setText(text)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ChatUnit()
    w.setText('HELLO')
    w.show()
    sys.exit(app.exec())