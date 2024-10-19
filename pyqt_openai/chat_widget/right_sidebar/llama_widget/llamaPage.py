from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextBrowser
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from pyqt_openai import SMALL_LABEL_PARAM
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.chat_widget.right_sidebar.llama_widget.listWidget import FileListWidget
from pyqt_openai.lang.translations import LangClass


class LlamaPage(QWidget):
    onDirectorySelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setFont(QFont(*SMALL_LABEL_PARAM))

        self.__listWidget = FileListWidget()
        self.__listWidget.clicked.connect(self.__setTextInBrowser)
        self.__listWidget.onDirectorySelected.connect(self.__onDirectorySelected)

        self.__txtBrowser = QTextBrowser()
        self.__txtBrowser.setPlaceholderText(
            LangClass.TRANSLATIONS[
                "This text browser shows selected file's content in the list."
            ]
        )
        self.__txtBrowser.setMaximumHeight(150)

        lay = QVBoxLayout()
        lay.addWidget(self.__listWidget)
        lay.addWidget(self.__txtBrowser)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

        self.setDirectory()

    def __onDirectorySelected(self):
        selected_dirname = self.__listWidget.getDirectory()
        self.onDirectorySelected.emit(selected_dirname)

    def __setTextInBrowser(self, txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            self.__txtBrowser.setText(f.read())

    def setDirectory(self):
        directory = CONFIG_MANAGER.get_general_property("llama_index_directory")
        self.__listWidget.setDirectory(directory, called_from_btn=False)
