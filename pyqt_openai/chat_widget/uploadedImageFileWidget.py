import os

from qtpy.QtCore import QByteArray, QBuffer
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QScrollArea

from pyqt_openai import PROMPT_IMAGE_SCALE
from pyqt_openai.lang.translations import LangClass


class UploadedImageFileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__delete_mode = False

    def __initUi(self):
        lbl = QLabel(LangClass.TRANSLATIONS['Uploaded Files (Only Images)'])
        self.__activateDeleteBtn = QPushButton(LangClass.TRANSLATIONS['Delete'])
        self.__activateDeleteBtn.setCheckable(True)
        self.__activateDeleteBtn.toggled.connect(self.__activateDelete)

        # TODO LANGUAGE
        self.__manualLbl = QLabel(LangClass.TRANSLATIONS['Click the image to delete'])
        self.__manualLbl.setStyleSheet('color: red;')

        lay = QHBoxLayout()
        lay.addWidget(lbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__manualLbl)
        lay.addWidget(self.__activateDeleteBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        imageWidget = QWidget()

        lay = QHBoxLayout()
        imageWidget.setLayout(lay)

        self.__imageArea = QScrollArea()
        self.__imageArea.setWidget(imageWidget)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__imageArea)

        self.setLayout(lay)

        self.__toggle(False)
        self.__imageArea.setWidgetResizable(True)

        self.__manualLbl.setVisible(False)

    def __toggle(self, f):
        self.__activateDeleteBtn.setEnabled(f)
        self.setVisible(f)

    def addFiles(self, filenames: list[str]):
        for filename in filenames:
            if os.path.splitext(filename)[-1] in ['.png', '.jpg', '.jpeg', '.gif']:
                buffer = QBuffer()
                buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                buffer.write(open(filename, 'rb').read())
                buffer = buffer.data()
                self.addImageBuffer(buffer)
        self.__toggle(True)

    def addImageBuffer(self, image_buffer: QByteArray):
        lay = self.__imageArea.widget().layout()
        lbl = QLabel()
        lbl.installEventFilter(self)
        pixmap = QPixmap()
        pixmap.loadFromData(image_buffer)
        pixmap = pixmap.scaled(*PROMPT_IMAGE_SCALE)
        lbl.setPixmap(pixmap)
        lay.addWidget(lbl)
        self.__toggle(True)

    def getImageBuffers(self):
        lay = self.__imageArea.widget().layout()
        buffers = []
        for i in range(lay.count()):
            lbl = lay.itemAt(i).widget()
            if not isinstance(lbl, QLabel):
                continue
            pixmap = lbl.pixmap()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.WriteOnly)

            # Save the pixmap to the buffer in PNG format
            pixmap.save(buffer, "PNG")

            # At this point, byte_array contains the image data
            print("Byte array length:", byte_array.size())

            # Convert QByteArray to bytes (if needed)
            image_bytes = byte_array.data()
            buffers.append(image_bytes)
        return buffers

    def __activateDelete(self):
        f = self.__activateDeleteBtn.isChecked()
        self.__manualLbl.setVisible(f)
        if f:
            self.__activateDeleteBtn.setText(LangClass.TRANSLATIONS['Cancel'])
        else:
            self.__activateDeleteBtn.setText(LangClass.TRANSLATIONS['Delete'])
        self.__delete_mode = f

    def clear(self):
        lay = self.__imageArea.widget().layout()
        for i in range(lay.count()):
            lay.itemAt(i).widget().deleteLater()
        self.__toggle(False)

    def eventFilter(self, obj, event):
        if isinstance(obj, QLabel):
            if event.type() == 2:
                if self.__delete_mode:
                    obj.deleteLater()
        return super().eventFilter(obj, event)



# if __name__ == "__main__":
#     import sys
#
#     app = QApplication(sys.argv)
#     w = UploadedImageFileWidget()
#     import pathlib
#
#     w.addFile([str(pathlib.Path(__file__).parent / 'a (1).png'),
#                str(pathlib.Path(__file__).parent / 'a (2).png'),
#                str(pathlib.Path(__file__).parent / 'a (3).png'),
#                 str(pathlib.Path(__file__).parent / 'a (4).png'),
#                 str(pathlib.Path(__file__).parent / 'a (5).png'),
#    ])
#     w.show()
#     sys.exit(app.exec())