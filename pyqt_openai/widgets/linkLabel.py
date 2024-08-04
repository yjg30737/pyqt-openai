import os

from qtpy.QtCore import Qt, QUrl
from qtpy.QtGui import QDesktopServices

from pyqt_openai.util.script import isUsingPyQt5
from pyqt_openai.widgets.svgLabel import SvgLabel


class LinkLabel(SvgLabel):
    def __init__(self):
        super().__init__()
        self.__url = '127.0.0.1'
        self.setStyleSheet('QLabel { color: blue;  } QLabel:hover { color: red; }')

    def setUrl(self, url):
        self.__url = url

    def mouseReleaseEvent(self, QMouseEvent):
        v = 1 if isUsingPyQt5() else Qt.MouseButton.LeftButton
        if QMouseEvent.button() == v:
            QDesktopServices.openUrl(QUrl(self.__url))
