import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from pyqt_openai.widgets.svgLabel import SvgLabel


class LinkLabel(SvgLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__url = '127.0.0.1'
        self.setStyleSheet('QLabel { color: blue;  } QLabel:hover { color: red; }')

    def setUrl(self, url):
        self.__url = url

    def mouseReleaseEvent(self, QMouseEvent):
        v = Qt.MouseButton.LeftButton
        if QMouseEvent.button() == v:
            QDesktopServices.openUrl(QUrl(self.__url))
