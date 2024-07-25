from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QLineEdit, QFrame, QPushButton, QHBoxLayout, QWidget

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import is_prompt_group_name_valid


class PromptGroupDirectInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['New Prompt'])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__name = QLineEdit()
        self.__name.setPlaceholderText(LangClass.TRANSLATIONS['Name'])
        self.__name.textChanged.connect(lambda x: self.__okBtn.setEnabled(x.strip() != ''))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS['OK'])
        self.__okBtn.clicked.connect(self.__accept)

        cancelBtn = QPushButton(LangClass.TRANSLATIONS['Cancel'])
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__name)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

    def getPromptGroupName(self):
        return self.__name.text()

    def __accept(self):
        exists_f = is_prompt_group_name_valid(self.__name.text())
        if exists_f:
            self.__name.setFocus()
            QMessageBox.warning(self, LangClass.TRANSLATIONS['Warning'], LangClass.TRANSLATIONS['Prompt name already exists.'])
            return
        else:
            self.accept()

