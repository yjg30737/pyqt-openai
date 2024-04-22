from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class ImageView(QGraphicsView):
    def __init__(self, mouse_tracking=False):
        super().__init__()
        self.__aspectRatioMode = Qt.KeepAspectRatio
        self.__initVal(mouse_tracking)
        self.__initUi()

    def __initVal(self, mouse_tracking):
        self._scene = QGraphicsScene()
        self._p = QPixmap()
        self._item = ''
        self.__mouse_tracking = mouse_tracking

    def __initUi(self):
        self.setMouseTracking(self.__mouse_tracking)

    def setFilename(self, filename: str):
        if filename == '':
            pass
        else:
            self._p = QPixmap(filename)
            self.setPixmap(self._p)

    def setPixmap(self, p):
        self._p = p
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