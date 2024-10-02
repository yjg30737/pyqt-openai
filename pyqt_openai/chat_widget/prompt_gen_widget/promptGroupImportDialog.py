import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QDialogButtonBox, QMessageBox, QDialog, QVBoxLayout, QTableWidget, QSplitter, \
    QWidget, QLabel, QAbstractItemView, QTableWidgetItem, QCheckBox

from pyqt_openai import JSON_FILE_EXT_LIST_STR, SENTENCE_PROMPT_GROUP_SAMPLE, FORM_PROMPT_GROUP_SAMPLE
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import validate_prompt_group_json, is_prompt_group_name_valid, showJsonSample, getSeparator
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.jsonEditor import JSONEditor


class PromptGroupImportDialog(QDialog):
    def __init__(self, prompt_type='form', parent=None):
        super().__init__(parent)
        self.__initVal(prompt_type)
        self.__initUi()

    def __initVal(self, prompt_type):
        self.__promptType = prompt_type
        self.__path = ''

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Import Prompt Group"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        findPathWidget = FindPathWidget()
        findPathWidget.setExtOfFiles(JSON_FILE_EXT_LIST_STR)
        findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS["Select a json file to import"])
        findPathWidget.added.connect(self.__setPath)

        btn = QPushButton(LangClass.TRANSLATIONS['What is the right form of json?'])
        btn.clicked.connect(self.__showJsonSample)

        self.__jsonSampleWidget = JSONEditor()

        sep = getSeparator('horizontal')

        allCheckBox = QCheckBox(LangClass.TRANSLATIONS['Select All'])
        self.__listWidget = CheckBoxListWidget()
        self.__listWidget.checkedSignal.connect(self.__toggleBtn)
        self.__listWidget.currentRowChanged.connect(lambda x: self.__showEntries(x))
        allCheckBox.stateChanged.connect(self.__listWidget.toggleState)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Prompt Group']))
        lay.addWidget(allCheckBox)
        lay.addWidget(self.__listWidget)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        self.__tableWidget = QTableWidget()
        self.__tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.__tableWidget.setColumnCount(2)
        self.__tableWidget.setHorizontalHeaderLabels([LangClass.TRANSLATIONS['Name'], LangClass.TRANSLATIONS['Value']])
        self.__tableWidget.setColumnWidth(0, 200)
        self.__tableWidget.setColumnWidth(1, 400)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Prompt Entry']))
        lay.addWidget(self.__tableWidget)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        splitter = QSplitter()
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([400, 600])
        splitter.setStyleSheet("QSplitterHandle {background-color: lightgray;}")

        self.__buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.__buttonBox.accepted.connect(self.__accept)
        self.__buttonBox.rejected.connect(self.reject)
        self.__buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        lay = QVBoxLayout()
        lay.addWidget(findPathWidget)
        lay.addWidget(sep)
        lay.addWidget(btn)
        lay.addWidget(splitter)
        lay.addWidget(self.__buttonBox)

        self.setLayout(lay)

        self.setMinimumSize(600, 350)

        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def __toggleBtn(self):
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.__listWidget.getCheckedRows()) > 0)

    def __showJsonSample(self):
        json_sample = FORM_PROMPT_GROUP_SAMPLE if self.__promptType == 'form' else SENTENCE_PROMPT_GROUP_SAMPLE
        showJsonSample(self.__jsonSampleWidget, json_sample)

    def __refreshTable(self):
        self.__tableWidget.clearContents()
        self.__tableWidget.setRowCount(0)

    def __setEntries(self, data):
        for d in data:
            name = d['name']
            content = d['content']
            self.__tableWidget.setRowCount(self.__tableWidget.rowCount() + 1)
            self.__tableWidget.setItem(self.__tableWidget.rowCount() - 1, 0, QTableWidgetItem(name))
            self.__tableWidget.setItem(self.__tableWidget.rowCount() - 1, 1, QTableWidgetItem(content))

    def __setPrompt(self, json_data):
        self.__listWidget.clear()

        self.__refreshTable()
        for prompt in json_data:
            name = prompt['name']
            data = prompt['data']
            self.__listWidget.addItem(name)
            self.__setEntries(data)

        self.__listWidget.item(0).setSelected(True)
        self.__data = json_data

    def __setPath(self, path):
        self.__path = path
        data = json.load(open(path))
        if validate_prompt_group_json(data):
            self.__buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.__setPrompt(json_data=data)
        else:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], LangClass.TRANSLATIONS['Check whether the file is a valid JSON file for importing.'])

    def __showEntries(self, r_idx):
        name = self.__listWidget.item(r_idx).text()
        self.__refreshTable()
        data = [d for d in self.__data if d['name'] == name][0]['data']
        self.__setEntries(data)

    def __accept(self):
        names = [self.__listWidget.item(r).text() for r in self.__listWidget.getCheckedRows()]
        new_names = list(filter(lambda x: is_prompt_group_name_valid(x), names))
        names_exist = list(filter(lambda x: x not in new_names, names))
        if names_exist:
            reply = QMessageBox.warning(self, LangClass.TRANSLATIONS['Warning'],
                                f"{LangClass.TRANSLATIONS['Following prompt names already exists. Would you like to import the rest?']}"
                                f"\n{', '.join(names_exist)}")
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                self.reject()
        self.__data = [d for d in self.__data if d['name'] in new_names]
        self.accept()

    def getSelected(self):
        return self.__data
