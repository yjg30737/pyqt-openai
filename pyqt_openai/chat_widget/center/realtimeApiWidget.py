from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QLabel, QVBoxLayout, QWidget

from pyqt_openai import LARGE_LABEL_PARAM


class RealtimeApiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        lay = QVBoxLayout()

        title = QLabel("Coming Soon...", self)
        title.setFont(QFont(*LARGE_LABEL_PARAM))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(title)

        self.setLayout(lay)
