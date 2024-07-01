from qtpy.QtCore import Qt, Signal, QSettings
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QFrame, QTextBrowser
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout

from pyqt_openai.pyqt_openai_data import LLAMAINDEX_WRAPPER
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.right_sidebar.llama_widget.listWidget import FileListWidget


class LlamaPage(QWidget):
    onDirectorySelected = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('PyQt LlamaIndex')

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        self.__listWidget = FileListWidget()
        self.__listWidget.clicked.connect(self.__setTextInBrowser)
        self.__listWidget.onDirectorySelected.connect(self.__onDirectorySelected)

        self.__txtBrowser = QTextBrowser()
        self.__txtBrowser.setPlaceholderText(LangClass.TRANSLATIONS["This text browser shows selected file's content in the list."])
        self.__txtBrowser.setMaximumHeight(150)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

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
        with open(txt_file, 'r', encoding='utf-8') as f:
            self.__txtBrowser.setText(f.read())

    def setDirectory(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)
        if self.__settings_ini.contains('llama_index_directory'):
            directory = self.__settings_ini.value('llama_index_directory', type=str)
            self.__listWidget.setDirectory(directory)
