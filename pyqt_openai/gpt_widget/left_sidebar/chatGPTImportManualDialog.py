from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from pyqt_openai import IMAGE_CHATGPT_IMPORT_MANUAL
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.normalImageView import NormalImageView


# TODO WILL_REMOVE_AFTER v1.2.X> - WILL BE REPLACED WITH ONLINE MANUAL
class ChatGPTImportManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['How to import your ChatGPT data'])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.__label1 = QLabel(
            LangClass.TRANSLATIONS['You can import "conversation.json" in zip file exported form ChatGPT.']
        )

        view1 = NormalImageView()
        view1.setFilename(IMAGE_CHATGPT_IMPORT_MANUAL)

        lay = QVBoxLayout()
        lay.addWidget(self.__label1)
        lay.addWidget(view1)

        self.setLayout(lay)