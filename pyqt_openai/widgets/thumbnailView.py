import os

from PyQt6.QtCore import Qt, QPointF, Signal
from PyQt6.QtGui import QPixmap, QColor, QBrush, QLinearGradient
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QApplication, QWidget, QHBoxLayout, \
    QFileDialog

from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.widgets.svgButton import SvgButton


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
        self.__aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio

        self.__factor = 1.1  # Zoom factor

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
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        # download the image
        saveBtn = SvgButton()
        saveBtn.setIcon('ico/save.svg')
        saveBtn.clicked.connect(self.__save)

        # zoom in
        zoomInBtn = SvgButton()
        zoomInBtn.setIcon('ico/add.svg')
        zoomInBtn.clicked.connect(self.__zoomIn)

        # zoom out
        zoomOutBtn = SvgButton()
        zoomOutBtn.setIcon('ico/delete.svg')
        zoomOutBtn.clicked.connect(self.__zoomOut)

        lay = QHBoxLayout()
        lay.addWidget(copyBtn)
        lay.addWidget(saveBtn)
        lay.addWidget(zoomInBtn)
        lay.addWidget(zoomOutBtn)

        self.__controlWidget = QWidget(self)
        self.__controlWidget.setLayout(lay)

        self.__controlWidget.hide()

    def __refreshSceneAndView(self):
        self._item = self._scene.addPixmap(self._p)
        self._item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        rect = self.sceneRect() \
            if (self._item.boundingRect().width() > self.sceneRect().width()) or (self._item.boundingRect().height() > self.sceneRect().height()) \
            else self._item.boundingRect()
        self.fitInView(rect, self.__aspectRatioMode)
        self.setScene(self._scene)

    def setFilename(self, filename: str):
        self._scene = QGraphicsScene()
        self._p = QPixmap(filename)
        self.__refreshSceneAndView()

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

    def __zoomIn(self):
        self.scale(self.__factor, self.__factor)

    def __zoomOut(self):
        self.scale(1 / self.__factor, 1 / self.__factor)

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
            self.setScene(self._scene)
        return super().resizeEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit(self._p)
        return super().mousePressEvent(e)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.Modifier.ControlModifier:
            # Check if Ctrl key is pressed
            if event.angleDelta().y() > 0:
                # Ctrl + wheel up, zoom in
                self.__zoomIn()
            else:
                # Ctrl + wheel down, zoom out
                self.__zoomOut()
            event.accept()  # Accept the event if Ctrl is pressed
        else:
            super().wheelEvent(event)  # Default behavior for other cases