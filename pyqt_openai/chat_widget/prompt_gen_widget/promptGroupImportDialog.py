import json

from PyQt5.QtWidgets import QPushButton
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QDialogButtonBox, QMessageBox, QDialog, QLabel, QVBoxLayout, QFrame

from pyqt_openai import JSON_FILE_EXT, SENTENCE_PROMPT_GROUP_SAMPLE, FORM_PROMPT_GROUP_SAMPLE
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import validate_prompt_group_json
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.jsonEditor import JSONEditor


class PromptGroupImportDialog(QDialog):
    def __init__(self, prompt_type='form'):
        super().__init__()
        self.__initVal(prompt_type)
        self.__initUi()

    def __initVal(self, prompt_type):
        self.__promptType = prompt_type
        self.__path = ''

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Import Prompt Group"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        findPathWidget = FindPathWidget()
        findPathWidget.setExtOfFiles(JSON_FILE_EXT)
        findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS["Select a json file to import"])
        findPathWidget.added.connect(self.__validateFile)

        btn = QPushButton(LangClass.TRANSLATIONS['What is the right form of json?'])
        btn.clicked.connect(self.__showJsonSample)

        self.__jsonSample = JSONEditor()

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.__buttonBox.accepted.connect(self.__accept)
        self.__buttonBox.rejected.connect(self.reject)
        self.__buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        lay = QVBoxLayout()
        lay.addWidget(findPathWidget)
        lay.addWidget(sep)
        lay.addWidget(btn)
        lay.addWidget(self.__buttonBox)

        self.setLayout(lay)

        self.setMinimumSize(600, 350)

    def __accept(self, path):
        print(path)

    def __showJsonSample(self):
        self.__jsonSample.setText(FORM_PROMPT_GROUP_SAMPLE if self.__promptType == 'form' else SENTENCE_PROMPT_GROUP_SAMPLE)
        self.__jsonSample.setReadOnly(True)
        self.__jsonSample.setMinimumSize(600, 350)
        self.__jsonSample.show()
        self.__jsonSample.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.__jsonSample.setWindowTitle(LangClass.TRANSLATIONS['JSON Sample'])

    def __validateFile(self, path):
        self.__path = path
        json_data = json.load(open(path))
        if validate_prompt_group_json(json_data, self.__promptType):
            self.__buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], LangClass.TRANSLATIONS['Check whether the file is a valid JSON file for importing.'])


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = PromptGroupImportDialog(prompt_type='sentence')
    w.show()
    sys.exit(app.exec())