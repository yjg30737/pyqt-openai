import os

from qtpy.QtGui import QPainter
from qtpy.QtSvg import QSvgRenderer
from qtpy.QtWidgets import QLabel

from pyqt_openai.pyqt_openai_data import ROOT_DIR

class SvgLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.__renderer = ''

    def paintEvent(self, e):
        painter = QPainter(self)
        if self.__renderer:
            self.__renderer.render(painter)
        return super().paintEvent(e)

    def setSvgFile(self, filename: str):
        filename = os.path.join(ROOT_DIR, filename)
        self.__renderer = QSvgRenderer(filename)
        self.resize(self.__renderer.defaultSize())
        length = max(self.sizeHint().width(), self.sizeHint().height())
        self.setFixedSize(length, length)