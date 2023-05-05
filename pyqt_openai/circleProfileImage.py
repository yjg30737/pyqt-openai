from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap, QPainter, QBitmap
from qtpy.QtWidgets import QLabel


class RoundedImage(QLabel):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__pixmap = ''
        self.__mask = ''

    def __initUi(self):
        pass

    def setImage(self, filename: str):
        # Load the image and set it as the pixmap for the label
        self.__pixmap = QPixmap(filename)
        self.__pixmap = self.__pixmap.scaled(self.__pixmap.width(), self.__pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # Create a mask the same shape as the image
        self.__mask = QBitmap(self.__pixmap.size())

        # Create a QPainter to draw the mask
        self.__painter = QPainter(self.__mask)
        self.__painter.setRenderHint(QPainter.Antialiasing)
        self.__painter.setRenderHint(QPainter.SmoothPixmapTransform)
        self.__painter.fillRect(self.__mask.rect(), Qt.white)

        # Draw a black, rounded rectangle on the mask
        self.__painter.setPen(Qt.black)
        self.__painter.setBrush(Qt.black)
        self.__painter.drawRoundedRect(self.__pixmap.rect(), self.__pixmap.size().width(),
                                       self.__pixmap.size().height())
        self.__painter.end()

        # Apply the mask to the image
        self.__pixmap.setMask(self.__mask)
        self.setPixmap(self.__pixmap)
        self.setScaledContents(True)