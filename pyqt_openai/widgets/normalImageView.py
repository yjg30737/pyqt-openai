from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView

if TYPE_CHECKING:
    from qtpy.QtGui import QResizeEvent
    from qtpy.QtWidgets import QGraphicsPixmapItem


class NormalImageView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.__aspectRatioMode: Qt.AspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio
        self.__initVal()

    def __initVal(self):
        self._scene = QGraphicsScene()
        self._p = QPixmap()
        self._item: str = ""

    def setFilename(
        self,
        filename: str,
    ):
        if filename == "":
            pass
        else:
            self._p = QPixmap(filename)
            self._setPixmap(self._p)

    def setPixmap(
        self,
        p: QPixmap,
    ):
        self._setPixmap(p)

    def _setPixmap(
        self,
        p: QPixmap,
    ):
        self._p: QPixmap = p
        self._scene: QGraphicsScene = QGraphicsScene()
        self._item: QGraphicsPixmapItem = self._scene.addPixmap(self._p)
        self.setScene(self._scene)
        self.fitInView(self._item, self.__aspectRatioMode)

    def setAspectRatioMode(
        self,
        mode: Qt.AspectRatioMode,
    ):
        self.__aspectRatioMode = mode

    def resizeEvent(
        self,
        event: QResizeEvent,
    ):
        if self._item:
            self.fitInView(self._item, self.__aspectRatioMode)
        return super().resizeEvent(event)
