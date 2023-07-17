import os
import requests

from qtpy.QtCore import Qt, QPointF, Signal
from qtpy.QtGui import QPixmap, QColor, QBrush, QLinearGradient
from qtpy.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QApplication, QWidget, QHBoxLayout, QFileDialog, QCheckBox, \
    QGraphicsProxyWidget

from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.svgButton import SvgButton


class ThumbnailView(QGraphicsView):
    clicked = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self._scene = QGraphicsScene()
        self._p = QPixmap()
        self._item = QGraphicsPixmapItem()
        self.__aspectRatioMode = Qt.KeepAspectRatio

    def __initUi(self):
        self.__setControlWidget()

        # set mouse event
        # to make buttons appear and apply gradient
        # above the top of an image when you hover the mouse cursor over it
        self.setMouseTracking(True)
        self.__defaultBrush = self.foregroundBrush()
        gradient = QLinearGradient(QPointF(0, 0), QPointF(0, self.viewport().height()))
        gradient.setColorAt(0, QColor(0, 0, 0, 200))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        self.__brush = QBrush(gradient)

        self.setMinimumSize(150, 150)

    def __setControlWidget(self):
        # copy the image
        copyBtn = SvgButton()
        copyBtn.setIcon('ico/copy_light.svg')
        copyBtn.clicked.connect(self.__copy)

        # download the image
        saveBtn = SvgButton()
        saveBtn.setIcon('ico/save_light.svg')
        saveBtn.clicked.connect(self.__save)

        lay = QHBoxLayout()
        lay.addWidget(copyBtn)
        lay.addWidget(saveBtn)

        self.__controlWidget = QWidget(self)
        self.__controlWidget.setLayout(lay)

        self.__controlWidget.hide()

    def __refreshSceneAndView(self):
        self._item = self._scene.addPixmap(self._p)
        self.fitInView(self.sceneRect(), self.__aspectRatioMode)
        self.setScene(self._scene)

    def setFilename(self, filename: str):
        self._scene = QGraphicsScene()
        self._p = QPixmap(filename)
        self.__refreshSceneAndView()

    def setUrl(self, url):
        self._scene = QGraphicsScene()
        response = requests.get(url)
        self._p.loadFromData(response.content)
        self.__refreshSceneAndView()
        return response.content

    def setContent(self, content):
        self._scene = QGraphicsScene()
        self._p.loadFromData(content)
        self.__refreshSceneAndView()

    def setPixmap(self, pixmap):
        self._scene = QGraphicsScene()
        self._p = pixmap
        self.__refreshSceneAndView()

    def setAspectRatioMode(self, mode):
        self.__aspectRatioMode = mode

    def __copy(self):
        QApplication.clipboard().setPixmap(self._p)

    def __save(self):
        filename = QFileDialog.getSaveFileName(self, LangClass.TRANSLATIONS['Save'], os.path.expanduser('~'), 'Image file (*.png)')
        if filename[0]:
            filename = filename[0]
            self._p.save(filename)

    def enterEvent(self, e):
        # Show the button when the mouse enters the view
        if self._item.pixmap().width():
            self.__controlWidget.move(self.rect().x(), self.rect().y())
            self.setForegroundBrush(self.__brush)
            self.__controlWidget.show()
        return super().enterEvent(e)

    def leaveEvent(self, e):
        # Hide the button when the mouse leaves the view
        self.__controlWidget.hide()
        self.setForegroundBrush(self.__defaultBrush)
        return super().leaveEvent(e)

    def resizeEvent(self, e):
        if self._item.pixmap().width():
            self.fitInView(self.sceneRect(), self.__aspectRatioMode)
            self.setScene(self._scene)
        return super().resizeEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit(self._p)
        return super().mousePressEvent(e)