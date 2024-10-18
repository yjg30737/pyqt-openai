from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from pyqt_openai import DEFAULT_LINK_COLOR, DEFAULT_LINK_HOVER_COLOR
from pyqt_openai.widgets.svgLabel import SvgLabel


class LinkLabel(SvgLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__url = "127.0.0.1"
        self.setStyleSheet(
            f"QLabel {{ color: {DEFAULT_LINK_COLOR};  }} QLabel:hover {{ color: {DEFAULT_LINK_HOVER_COLOR}; }}"
        )

    def setUrl(self, url):
        self.__url = url

    def mouseReleaseEvent(self, QMouseEvent):
        v = Qt.MouseButton.LeftButton
        if QMouseEvent.button() == v:
            QDesktopServices.openUrl(QUrl(self.__url))
