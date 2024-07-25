from PyQt5.QtWidgets import QApplication
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QLabel, QVBoxLayout, QFrame, QSplitter, QSizePolicy

from pyqt_openai import JSON_FILE_EXT, SENTENCE_PROMPT_GROUP_SAMPLE, FORM_PROMPT_GROUP_SAMPLE
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.jsonEditor import JSONEditor


class PromptGroupImportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Import Prompt Group"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        findPathWidget = FindPathWidget()
        findPathWidget.setExtOfFiles(JSON_FILE_EXT)
        findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS["Select a json file to import"])
        findPathWidget.added.connect(self.__accepted)

        lbl = QLabel(LangClass.TRANSLATIONS['Right form of json to be imported'])

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        formSample = JSONEditor()
        formSample.setText(str(FORM_PROMPT_GROUP_SAMPLE))
        formSample.setReadOnly(True)

        sentenceSample = JSONEditor()
        sentenceSample.setText(str(SENTENCE_PROMPT_GROUP_SAMPLE))
        sentenceSample.setReadOnly(True)

        self.__splitter = QSplitter()
        self.__splitter.addWidget(formSample)
        self.__splitter.addWidget(sentenceSample)
        self.__splitter.setHandleWidth(1)
        self.__splitter.setChildrenCollapsible(False)
        self.__splitter.setSizes([500, 500])
        self.__splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        self.__splitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        lay = QVBoxLayout()
        lay.addWidget(findPathWidget)
        lay.addWidget(sep)
        lay.addWidget(lbl)
        lay.addWidget(self.__splitter)

        self.setLayout(lay)

        self.setMinimumSize(600, 350)

    def __accepted(self, path):
        print(f'Accepted: {path}')


# if __name__ == "__main__":
#     import sys
#
#     app = QApplication(sys.argv)
#     w = PromptGroupImportDialog()
#     w.show()
#     sys.exit(app.exec())