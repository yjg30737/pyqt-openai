from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QFrame, QTextBrowser
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout

from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.right_sidebar.llama_widget.listWidget import FileListWidget
from pyqt_openai.util.llamapage_script import GPTLLamaIndexClass


class LlamaPage(QWidget):
    onDirectorySelected = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initVal(self, db, ini_etc_dict, model_data):
        self.__gptLLamaIndexClass = GPTLLamaIndexClass()

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
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        lay = QVBoxLayout()
        lay.addWidget(self.__listWidget)
        lay.addWidget(self.__txtBrowser)
        lay.setAlignment(Qt.AlignTop)

        self.setLayout(lay)

    def __onDirectorySelected(self):
        selected_dirname = self.__listWidget.getDir()
        self.onDirectorySelected.emit(selected_dirname)

    def __setTextInBrowser(self, txt_file):
        with open(txt_file, 'r', encoding='utf-8') as f:
            self.__txtBrowser.setText(f.read())
