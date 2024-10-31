from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from pyqt_openai import LARGE_LABEL_PARAM


class RealtimeApiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        lay = QVBoxLayout()

        title = QLabel('Coming Soon...', self)
        title.setFont(QFont(*LARGE_LABEL_PARAM))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(title)

        self.setLayout(lay)