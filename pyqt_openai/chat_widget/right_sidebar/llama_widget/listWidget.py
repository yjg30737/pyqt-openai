import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QListWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSpacerItem,
    QPushButton,
    QSizePolicy,
    QFileDialog,
)

from pyqt_openai import TEXT_FILE_EXT_LIST, QFILEDIALOG_DEFAULT_DIRECTORY
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import getSeparator


class FileListWidget(QWidget):
    itemUpdate = Signal(bool)
    onDirectorySelected = Signal()
    clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__dirLblPrefix = LangClass.TRANSLATIONS["Directory"]
        self.__curDirName = ""

    def __initUi(self):
        lbl = QLabel(LangClass.TRANSLATIONS["Files"])
        setDirBtn = QPushButton(LangClass.TRANSLATIONS["Set Directory"])
        setDirBtn.clicked.connect(self.setDirectory)
        self.__dirLbl = QLabel(self.__dirLblPrefix)

        lay = QHBoxLayout()
        lay.addWidget(lbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(setDirBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__listWidget = QListWidget()
        self.__listWidget.itemClicked.connect(self.__sendDirectory)

        sep = getSeparator("horizontal")

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(sep)
        lay.addWidget(self.__dirLbl)
        lay.addWidget(self.__listWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def setDirectory(self, directory=None, called_from_btn=True):
        try:
            if called_from_btn:
                if not directory:
                    directory = QFileDialog.getExistingDirectory(
                        self,
                        LangClass.TRANSLATIONS["Select Directory"],
                        QFILEDIALOG_DEFAULT_DIRECTORY,
                        QFileDialog.Option.ShowDirsOnly,
                    )
            if directory:
                self.__listWidget.clear()
                filenames = list(
                    filter(
                        lambda x: os.path.splitext(x)[-1] in TEXT_FILE_EXT_LIST,
                        os.listdir(directory),
                    )
                )
                self.__listWidget.addItems(filenames)
                self.itemUpdate.emit(len(filenames) > 0)
                self.__curDirName = directory
                self.__dirLbl.setText(self.__curDirName.split("/")[-1])

                self.__listWidget.setCurrentRow(0)
                # activate event as clicking first item (because this selects the first item anyway)
                self.clicked.emit(
                    os.path.join(
                        self.__curDirName, self.__listWidget.currentItem().text()
                    )
                )
                self.onDirectorySelected.emit()
        except Exception as e:
            print(e)

    def getDirectory(self):
        return self.__curDirName

    def __sendDirectory(self, item):
        self.clicked.emit(os.path.join(self.__curDirName, item.text()))
