from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QCheckBox,
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel,
)

from pyqt_openai import SENTENCE_PROMPT_GROUP_SAMPLE, FORM_PROMPT_GROUP_SAMPLE
from pyqt_openai.chat_widget.prompt_gen_widget.promptCsvRightFormSampleDialog import PromptCSVRightFormSampleDialog
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import showJsonSample
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget
from pyqt_openai.widgets.jsonEditor import JSONEditor


class PromptGroupExportDialog(QDialog):
    def __init__(self, data, prompt_type="form", ext='.json', parent=None):
        super().__init__(parent)
        self.__initVal(data, prompt_type, ext)
        self.__initUi()

    def __initVal(self, data, prompt_type, ext):
        self.__data = data
        self.__promptType = prompt_type
        self.__ext = ext

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Export Prompt Group"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        btnText = LangClass.TRANSLATIONS["Preview of the JSON format to be created after export"] if self.__ext == '.json' else LangClass.TRANSLATIONS["Preview of the CSV format to be created after export"]
        btn = QPushButton(btnText)

        if self.__ext == '.json':
            btn.clicked.connect(self.__showJsonSample)
            self.__jsonSampleWidget = JSONEditor()
        elif self.__ext == '.csv':
            btn.clicked.connect(self.__showCSVSample)

        allCheckBox = QCheckBox(LangClass.TRANSLATIONS["Select All"])
        self.__listWidget = CheckBoxListWidget()
        self.__listWidget.addItems([d["name"] for d in self.__data])
        self.__listWidget.checkedSignal.connect(self.__toggledBtn)
        allCheckBox.stateChanged.connect(self.__listWidget.toggleState)

        self.__buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.__buttonBox.accepted.connect(self.accept)
        self.__buttonBox.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(
            QLabel(LangClass.TRANSLATIONS["Select the prompts you want to export."])
        )
        lay.addWidget(allCheckBox)
        lay.addWidget(self.__listWidget)
        lay.addWidget(btn)
        lay.addWidget(self.__buttonBox)
        self.setLayout(lay)

        self.setLayout(lay)

        allCheckBox.setChecked(True)

    def __toggledBtn(self):
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            len(self.__listWidget.getCheckedRows()) > 0
        )

    def __showJsonSample(self):
        json_sample = (
            FORM_PROMPT_GROUP_SAMPLE
            if self.__promptType == "form"
            else SENTENCE_PROMPT_GROUP_SAMPLE
        )
        showJsonSample(self.__jsonSampleWidget, json_sample)

    def __showCSVSample(self):
        dialog = PromptCSVRightFormSampleDialog(self)
        dialog.exec()

    def getSelected(self):
        """
        Get selected prompt group names.
        The data is used to export the selected prompt groups.
        This function is giving names instead of ids because the name field is unique anyway.
        """
        names = [
            self.__listWidget.item(r).text() for r in self.__listWidget.getCheckedRows()
        ]
        result = [d for d in self.__data if d["name"] in names]
        return result
