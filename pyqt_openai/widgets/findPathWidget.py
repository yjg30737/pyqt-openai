from __future__ import annotations

import os
import subprocess

from typing import TYPE_CHECKING, cast

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QAction
from qtpy.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton, QWidget

from pyqt_openai.lang.translations import LangClass

if TYPE_CHECKING:
    from qtpy.QtCore import QPoint
    from qtpy.QtGui import QMouseEvent



class FindPathLineEdit(QLineEdit):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setMouseTracking(True)
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepareMenu)

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ):
        self.__showToolTip()
        return super().mouseMoveEvent(event)

    def __showToolTip(self):
        text = self.text()
        text_width = self.fontMetrics().boundingRect(text).width()

        if text_width > self.width():
            self.setToolTip(text)
        else:
            self.setToolTip("")

    def __prepareMenu(
        self,
        pos: QPoint,
    ):
        menu = QMenu(self)
        openDirAction = QAction(LangClass.TRANSLATIONS["Open Path"])
        openDirAction.setEnabled(self.text().strip() != "")
        openDirAction.triggered.connect(self.__openPath)
        menu.addAction(openDirAction)
        menu.exec(self.mapToGlobal(pos))

    def __openPath(self):
        filename = self.text()
        path = filename.replace("/", "\\")
        subprocess.Popen(r'explorer /select,"' + path + '"')


class FindPathWidget(QWidget):
    findClicked = Signal()
    added = Signal(str)

    def __init__(
        self,
        default_filename: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initVal()
        self.__initUi(default_filename)

    def __initVal(self):
        self.__ext_of_files: str = ""
        self.__directory: bool = False

    def __initUi(
        self,
        default_filename: str = "",
    ):
        self.__pathLineEdit: FindPathLineEdit = FindPathLineEdit()
        if default_filename:
            self.__pathLineEdit.setText(default_filename)

        self.__pathFindBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["Find..."])

        self.__pathFindBtn.clicked.connect(self.__find)

        self.__pathLineEdit.setMaximumHeight(self.__pathFindBtn.sizeHint().height())

        lay = QHBoxLayout()
        lay.addWidget(self.__pathLineEdit)
        lay.addWidget(self.__pathFindBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def setLabel(
        self,
        text: str,
    ):
        cast(QHBoxLayout, self.layout()).insertWidget(0, QLabel(text))

    def setExtOfFiles(
        self,
        ext_of_files: str,
    ):
        self.__ext_of_files = ext_of_files

    def getLineEdit(self) -> FindPathLineEdit:
        return self.__pathLineEdit

    def getButton(self) -> QPushButton:
        return self.__pathFindBtn

    def getFileName(self) -> str:
        return self.__pathLineEdit.text()

    def setCustomFind(self, f: bool):
        if f:
            self.__pathFindBtn.clicked.disconnect(self.__find)
            self.__pathFindBtn.clicked.connect(self.__customFind)

    def __customFind(self):
        self.findClicked.emit()

    def __find(self):
        if self.isForDirectory():
            filename = QFileDialog.getExistingDirectory(
                self,
                LangClass.TRANSLATIONS["Open Directory"],
                os.path.expanduser("~"),
                QFileDialog.Option.ShowDirsOnly,
            )
            if filename:
                pass
            else:
                return
        else:
            str_exp_files_to_open = (
                self.__ext_of_files if self.__ext_of_files else "All Files (*.*)"
            )
            filename = QFileDialog.getOpenFileName(
                self,
                LangClass.TRANSLATIONS["Find"],
                os.path.expanduser("~"),
                str_exp_files_to_open,
            )
            if not filename[0] or not filename[0].strip():
                return
            filename = filename[0]
        self.__pathLineEdit.setText(filename)
        self.added.emit(filename)

    def setAsDirectory(
        self,
        f: bool,
    ):
        self.__directory = f

    def isForDirectory(self) -> bool:
        return self.__directory
