from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import QUrl, Qt
from qtpy.QtGui import QDesktopServices

from pyqt_openai import DEFAULT_LINK_COLOR, DEFAULT_LINK_HOVER_COLOR
from pyqt_openai.widgets.svgLabel import SvgLabel

if TYPE_CHECKING:
    from qtpy.QtGui import QMouseEvent
    from qtpy.QtWidgets import QWidget


class LinkLabel(SvgLabel):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__url: str = "127.0.0.1"
        self.setStyleSheet(
            f"QLabel {{ color: {DEFAULT_LINK_COLOR};  }} QLabel:hover {{ color: {DEFAULT_LINK_HOVER_COLOR}; }}",
        )

    def setUrl(
        self,
        url: str,
    ):
        self.__url = url

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ):
        v: Qt.MouseButton = Qt.MouseButton.LeftButton
        if event.button() == v:
            QDesktopServices.openUrl(QUrl(self.__url))
