import os

from PyQt5.QtGui import QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QLabel


class SvgLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.__renderer = ''

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.restore()
        if self.__renderer:
            self.__renderer.render(painter)
        return super().paintEvent(e)

    def setSvgFile(self, filename: str):
        filename = os.path.join(os.path.dirname(__file__), filename)
        self.__renderer = QSvgRenderer(filename)
        self.resize(self.__renderer.defaultSize())
        length = max(self.sizeHint().width(), self.sizeHint().height())
        self.setFixedSize(length, length)