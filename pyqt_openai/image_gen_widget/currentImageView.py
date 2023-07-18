from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView, QPushButton


class CurrentImageView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.__aspectRatioMode = Qt.KeepAspectRatio
        self.__gradient_enabled = False
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self._scene = QGraphicsScene()
        self._p = QPixmap()
        self._item = ''

    def __initUi(self):
        self.setMouseTracking(True)

    def setFilename(self, filename: str):
        self._p = QPixmap(filename)
        self._scene = QGraphicsScene()
        self._item = self._scene.addPixmap(self._p)

        self.setScene(self._scene)
        self.fitInView(self._item, self.__aspectRatioMode)

    def setAspectRatioMode(self, mode):
        self.__aspectRatioMode = mode

    def resizeEvent(self, e):
        if self._item:
            self.fitInView(self.sceneRect(), self.__aspectRatioMode)
        return super().resizeEvent(e)