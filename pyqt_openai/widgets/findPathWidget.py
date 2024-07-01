import os

import subprocess

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel, \
    QFileDialog, QAction, QLineEdit, QMenu

from pyqt_openai.res.language_dict import LangClass


class FindPathLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setMouseTracking(True)
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepareMenu)

    def mouseMoveEvent(self, e):
        self.__showToolTip()
        return super().mouseMoveEvent(e)

    def __showToolTip(self):
        text = self.text()
        text_width = self.fontMetrics().boundingRect(text).width()

        if text_width > self.width():
            self.setToolTip(text)
        else:
            self.setToolTip('')

    def __prepareMenu(self, pos):
        menu = QMenu(self)
        openDirAction = QAction(LangClass.TRANSLATIONS['Open Path'])
        openDirAction.setEnabled(self.text().strip() != '')
        openDirAction.triggered.connect(self.__openPath)
        menu.addAction(openDirAction)
        menu.exec(self.mapToGlobal(pos))

    def __openPath(self):
        filename = self.text()
        path = filename.replace('/', '\\')
        subprocess.Popen(r'explorer /select,"' + path + '"')


class FindPathWidget(QWidget):
    findClicked = Signal()
    added = Signal(str)

    def __init__(self, default_filename: str = ''):
        super().__init__()
        self.__initVal()
        self.__initUi(default_filename)

    def __initVal(self):
        self.__ext_of_files = ''
        self.__directory = False

    def __initUi(self, default_filename: str = ''):
        self.__pathLineEdit = FindPathLineEdit()
        if default_filename:
            self.__pathLineEdit.setText(default_filename)

        self.__pathFindBtn = QPushButton(LangClass.TRANSLATIONS['Find...'])

        self.__pathFindBtn.clicked.connect(self.__find)

        self.__pathLineEdit.setMaximumHeight(self.__pathFindBtn.sizeHint().height())

        lay = QHBoxLayout()
        lay.addWidget(self.__pathLineEdit)
        lay.addWidget(self.__pathFindBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def setLabel(self, text):
        self.layout().insertWidget(0, QLabel(text))

    def setExtOfFiles(self, ext_of_files):
        self.__ext_of_files = ext_of_files

    def getLineEdit(self):
        return self.__pathLineEdit

    def getButton(self):
        return self.__pathFindBtn

    def getFileName(self):
        return self.__pathLineEdit.text()

    def setCustomFind(self, f: bool):
        if f:
            self.__pathFindBtn.clicked.disconnect(self.__find)
            self.__pathFindBtn.clicked.connect(self.__customFind)

    def __customFind(self):
        self.findClicked.emit()

    def __find(self):
        if self.isForDirectory():
            filename = QFileDialog.getExistingDirectory(self, 'Open Directory', os.path.expanduser('~'), QFileDialog.Option.ShowDirsOnly)
            if filename:
                pass
            else:
                return
        else:
            str_exp_files_to_open = self.__ext_of_files if self.__ext_of_files else 'All Files (*.*)'
            filename = QFileDialog.getOpenFileName(self, 'Find', os.path.expanduser('~'), str_exp_files_to_open)
            if filename[0]:
                filename = filename[0]
            else:
                return
        self.__pathLineEdit.setText(filename)
        self.added.emit(filename)

    def setAsDirectory(self, f: bool):
        self.__directory = f

    def isForDirectory(self) -> bool:
        return self.__directory
