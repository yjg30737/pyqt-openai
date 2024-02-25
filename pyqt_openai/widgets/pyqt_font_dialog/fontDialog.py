from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, \
    QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

from .fontWidget import FontWidget


class FontDialog(QDialog):
    def __init__(self, font: QFont = QFont('Arial', 10), title='Font'):
        super().__init__()
        self.__current_font = font
        self.__initUi(font=font, title=title)

    def __initUi(self, font: QFont, title):
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.__fontWidget = FontWidget(font=font)
        self.__fontWidget.layout().setContentsMargins(0, 0, 0, 0)

        okBtn = QPushButton('OK')
        cancelBtn = QPushButton('Cancel')

        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignRight)
        lay.addWidget(okBtn)
        lay.addWidget(cancelBtn)
        lay.setContentsMargins(0, 2, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__fontWidget)
        lay.addWidget(okCancelWidget)
        self.setLayout(lay)

    def getFont(self):
        return self.__fontWidget.getFont()