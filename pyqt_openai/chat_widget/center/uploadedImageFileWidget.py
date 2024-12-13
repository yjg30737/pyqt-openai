from __future__ import annotations

import os

from typing import TYPE_CHECKING

from qtpy.QtCore import QBuffer, QByteArray, Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from pyqt_openai import IMAGE_FILE_EXT_LIST, PROMPT_IMAGE_SCALE
from pyqt_openai.lang.translations import LangClass

if TYPE_CHECKING:
    from qtpy.QtCore import QEvent, QObject
    from qtpy.QtWidgets import QLayout


class UploadedImageFileWidget(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__delete_mode: bool = False
        self.__original_pixmaps: list[QPixmap] = []  # Array of original images

    def __initUi(self):
        lbl = QLabel(LangClass.TRANSLATIONS["Uploaded Files (Only Images)"])
        self.__activateDeleteBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["Delete"])
        self.__activateDeleteBtn.setCheckable(True)
        self.__activateDeleteBtn.toggled.connect(self.__activateDelete)

        self.__manualLbl: QLabel = QLabel(LangClass.TRANSLATIONS["Click the image to delete"])
        self.__manualLbl.setStyleSheet("color: red;")

        hlay = QHBoxLayout()
        hlay.addWidget(lbl)
        hlay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        hlay.addWidget(self.__manualLbl)
        hlay.addWidget(self.__activateDeleteBtn)
        hlay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(hlay)

        imageWidget = QWidget()

        hlay = QHBoxLayout()
        hlay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        imageWidget.setLayout(hlay)

        self.__imageArea: QScrollArea = QScrollArea()
        self.__imageArea.setWidget(imageWidget)

        vlay = QVBoxLayout()
        vlay.addWidget(topWidget)
        vlay.addWidget(self.__imageArea)

        self.setLayout(vlay)

        self.__toggle(False)
        self.__imageArea.setWidgetResizable(True)

        self.__manualLbl.setVisible(False)

    def __toggle(self, f: bool) -> None:
        self.__activateDeleteBtn.setEnabled(f)
        self.setVisible(f)

    def addFiles(self, filenames: list[str]):
        for filename in filenames:
            if os.path.splitext(filename)[-1] in IMAGE_FILE_EXT_LIST:
                buffer = QBuffer()
                buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                buffer.write(open(filename, "rb").read())
                buffer_data = buffer.data()
                self.addImageBuffer(buffer_data)
        self.__toggle(True)

    def getLayout(self) -> QHBoxLayout | QLayout:
        layout = self.__imageArea.widget().layout()
        if not layout:
            layout = QHBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.__imageArea.widget().setLayout(layout)
        return layout

    def addImageBuffer(self, image_buffer: QByteArray):
        lay = self.getLayout()
        lbl = QLabel()
        lbl.installEventFilter(self)
        pixmap = QPixmap()
        pixmap.loadFromData(image_buffer)
        self.__original_pixmaps.append(pixmap)
        pixmap = pixmap.scaled(*PROMPT_IMAGE_SCALE)
        lbl.setPixmap(pixmap)
        lay.addWidget(lbl)
        self.__toggle(True)

    def getImageBuffers(self) -> list[bytes | bytearray | memoryview[int]]:
        buffers = []
        # Make a copy of the original images
        for pixmap in self.__original_pixmaps:
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)

            # Save the pixmap to the buffer
            pixmap.save(buffer, "PNG")

            # Convert the buffer to bytes
            image_bytes = byte_array.data()
            buffers.append(image_bytes)

        self.__original_pixmaps = []

        return buffers

    def __activateDelete(self):
        f = self.__activateDeleteBtn.isChecked()
        self.__manualLbl.setVisible(f)
        if f:
            self.__activateDeleteBtn.setText(LangClass.TRANSLATIONS["Cancel"])
        else:
            self.__activateDeleteBtn.setText(LangClass.TRANSLATIONS["Delete"])
        self.__delete_mode = f

    def clear(self):
        lay = self.getLayout()
        for i in range(lay.count()):
            lay_item_i = lay.itemAt(i)
            assert lay_item_i is not None, "lay_item_i is None"
            widget = lay_item_i.widget()
            assert widget is not None, f"widget is None at index {i}"
            widget.deleteLater()
        self.__toggle(False)

    def eventFilter(
        self,
        obj: QObject,
        event: QEvent,
    ) -> bool:
        if isinstance(obj, QLabel):
            if event.type() == 2:
                if self.__delete_mode:
                    obj.deleteLater()
                    if self.getLayout().count() == 1:
                        self.__toggle(False)
        return super().eventFilter(obj, event)
