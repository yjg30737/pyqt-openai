from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea

from pyqt_openai import CONTEXT_DELIMITER
from pyqt_openai.widgets.linkLabel import LinkLabel


class DallEHome(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel('Welcome to DALL-E Page !', self)
        title.setFont(QFont('Arial', 32))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel('Generate images with DALL-E.' + CONTEXT_DELIMITER)

        description.setFont(QFont('Arial', 16))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)