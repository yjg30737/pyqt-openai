from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtGui import QPainter
from qtpy.QtSvg import QSvgRenderer
from qtpy.QtWidgets import QLabel

if TYPE_CHECKING:
    from qtpy.QtGui import QPaintEvent
    from qtpy.QtWidgets import QWidget


class SvgLabel(QLabel):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__renderer: QSvgRenderer | None = None

    def paintEvent(
        self,
        event: QPaintEvent,
    ):
        painter = QPainter(self)
        if self.__renderer:
            self.__renderer.render(painter)
        return super().paintEvent(event)

    def setSvgFile(
        self,
        filename: str,
    ):
        self.__renderer = QSvgRenderer(filename)
        self.resize(self.__renderer.defaultSize())
        length = max(self.sizeHint().width(), self.sizeHint().height())
        self.setFixedSize(length, length)
