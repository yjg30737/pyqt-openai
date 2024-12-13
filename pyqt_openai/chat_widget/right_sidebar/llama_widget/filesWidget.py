from __future__ import annotations

import os

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from pyqt_openai import QFILEDIALOG_DEFAULT_DIRECTORY
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import getSeparator


class FilesWidget(QWidget):
    itemUpdate = Signal(bool)
    onDirectorySelected = Signal()
    clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__directory_label_prefix = LangClass.TRANSLATIONS["Directory"]
        self.__current_directory_name = ""
        self.__extension = CONFIG_MANAGER.get_general_property("llama_index_supported_formats")

    def __initUi(self):
        lbl = QLabel(LangClass.TRANSLATIONS["Files"])
        setDirBtn = QPushButton(LangClass.TRANSLATIONS["Set Directory"])
        setDirBtn.clicked.connect(self.setDirectory)
        self.__dirLbl = QLabel(self.__directory_label_prefix)

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

    def setExtension(self, ext):
        # Set extension
        self.__extension = ext
        CONFIG_MANAGER.set_general_property("llama_index_supported_formats", ext)

        # Refresh list based on new extension
        self.__listWidget.clear()
        self.setDirectory(self.__current_directory_name, called_from_btn=False)

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
                        lambda x: os.path.splitext(x)[-1] in self.__extension,
                        os.listdir(directory),
                    ),
                )
                self.__listWidget.addItems(filenames)
                self.itemUpdate.emit(len(filenames) > 0)
                self.__current_directory_name = directory
                self.__dirLbl.setText(self.__current_directory_name.split("/")[-1])

                self.__listWidget.setCurrentRow(0)
                # activate event as clicking first item (because this selects the first item anyway)
                self.clicked.emit(
                    os.path.join(
                        self.__current_directory_name, self.__listWidget.currentItem().text(),
                    ),
                )
                self.onDirectorySelected.emit()
        except Exception as e:
            print(e)

    def getDirectory(self):
        return self.__current_directory_name

    def __sendDirectory(self, item):
        self.clicked.emit(os.path.join(self.__current_directory_name, item.text()))
