from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QLineEdit, QPushButton, QHBoxLayout, QWidget, \
    QMessageBox

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import is_prompt_entry_name_valid, getSeparator


class PromptEntryDirectInputDialog(QDialog):
    def __init__(self, group_id, parent=None):
        super().__init__(parent)
        self.__initVal(group_id)
        self.__initUi()

    def __initVal(self, group_id):
        self.__group_id = group_id

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['New Prompt'])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__name = QLineEdit()
        self.__name.setPlaceholderText(LangClass.TRANSLATIONS['Name'])
        self.__name.textChanged.connect(lambda x: self.__okBtn.setEnabled(x.strip() != ''))

        self.__content = QPlainTextEdit()
        self.__content.setPlaceholderText(LangClass.TRANSLATIONS['Content'])
        self.__content.textChanged.connect(lambda x: self.__name.text().strip() != '' and self.__okBtn.setEnabled(x.strip() != ''))

        sep = getSeparator('horizontal')

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
        lay.addWidget(self.__content)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

    def getPromptName(self):
        return self.__name.text()

    def __accept(self):
        exists_f = is_prompt_entry_name_valid(self.__group_id, self.__name.text())
        if exists_f:
            self.__name.setFocus()
            QMessageBox.warning(self, LangClass.TRANSLATIONS['Warning'], LangClass.TRANSLATIONS['Entry name already exists.'])
            return
        else:
            self.accept()