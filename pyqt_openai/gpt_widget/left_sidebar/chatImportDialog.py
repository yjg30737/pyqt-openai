import json
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QAbstractItemView, QSpinBox, QTableWidgetItem, QMessageBox, QGroupBox, QLabel, \
    QDialogButtonBox, \
    QCheckBox, QDialog, QVBoxLayout, QPushButton

from pyqt_openai import JSON_FILE_EXT_LIST_STR, THREAD_ORDERBY, HOW_TO_EXPORT_CHATGPT_CONVERSATION_HISTORY_URL
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import get_chatgpt_data_for_import, get_chatgpt_data_for_preview
from pyqt_openai.widgets.checkBoxTableWidget import CheckBoxTableWidget
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.linkLabel import LinkLabel


class ChatImportDialog(QDialog):
    def __init__(self, import_type='general', parent=None):
        super().__init__(parent)
        self.__initVal(import_type)
        self.__initUi()

    def __initVal(self, import_type):
        self.__import_type = import_type
        # Get the most recent n conversation threads
        self.__most_recent_n = 10
        # Data to be imported
        self.__data = []

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Import"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        findPathWidget = FindPathWidget()
        findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS['Select a json file to import'])
        findPathWidget.setExtOfFiles(JSON_FILE_EXT_LIST_STR)
        findPathWidget.added.connect(self.__setPath)

        self.__chkBoxMostRecent = QCheckBox(LangClass.TRANSLATIONS['Get most recent'])
        self.__chkBoxMostRecent.setChecked(False)

        self.__mostRecentNSpinBox = QSpinBox()
        self.__mostRecentNSpinBox.setRange(1, 10000)
        self.__mostRecentNSpinBox.setValue(self.__most_recent_n)
        self.__mostRecentNSpinBox.setEnabled(False)

        self.__chkBoxMostRecent.stateChanged.connect(lambda state: self.__mostRecentNSpinBox.setEnabled(Qt.CheckState(state) == Qt.CheckState.Checked))

        importOptionsGrpBox = QGroupBox(LangClass.TRANSLATIONS['Import Options'])
        lay = QVBoxLayout()
        lay.addWidget(self.__chkBoxMostRecent)
        lay.addWidget(self.__mostRecentNSpinBox)
        importOptionsGrpBox.setLayout(lay)

        self.__checkBoxTableWidget = CheckBoxTableWidget()
        self.__checkBoxTableWidget.setColumnCount(0)
        self.__checkBoxTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.__allCheckBox = QCheckBox(LangClass.TRANSLATIONS['Select All'])
        self.__allCheckBox.stateChanged.connect(self.__checkBoxTableWidget.toggleState)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Select the threads you want to import.']))
        lay.addWidget(self.__allCheckBox)
        lay.addWidget(self.__checkBoxTableWidget)

        self.__dataGrpBox = QGroupBox(LangClass.TRANSLATIONS['Content'])
        self.__dataGrpBox.setLayout(lay)
        self.__dataGrpBox.setEnabled(False)

        self.__buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.__buttonBox.accepted.connect(self.accept)
        self.__buttonBox.rejected.connect(self.reject)
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        manual_lbl = QLabel(LangClass.TRANSLATIONS['You can import a JSON file created through the export feature.'])
        lay = QVBoxLayout()
        lay.addWidget(manual_lbl)

        if self.__import_type == 'chatgpt':
            viewManualLbl = LinkLabel()
            viewManualLbl.setText(LangClass.TRANSLATIONS['How to import your ChatGPT data'])
            viewManualLbl.setUrl(HOW_TO_EXPORT_CHATGPT_CONVERSATION_HISTORY_URL)
            lay.addWidget(viewManualLbl)

        manualWidget = QWidget()
        manualWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(findPathWidget)
        lay.addWidget(importOptionsGrpBox)
        lay.addWidget(manualWidget)
        lay.addWidget(self.__dataGrpBox)
        lay.addWidget(self.__buttonBox)

        self.setLayout(lay)

        self.resize(800, 600)

        self.__checkBoxTableWidget.checkedSignal.connect(self.__toggleBtn)
        self.__allCheckBox.stateChanged.connect(self.__toggleBtn)

    def __toggleBtn(self):
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.__checkBoxTableWidget.getCheckedRows()) > 0)

    def __setPath(self, path):
        try:
            most_recent_n = self.__mostRecentNSpinBox.value() if self.__chkBoxMostRecent.isChecked() else None
            if self.__import_type == 'general':
                self.__path = path
                self.__data = json.load(open(path))
                data_length = len(self.__data) if most_recent_n is None else most_recent_n
                self.__data = self.__data[:data_length]
                columns = [
                    'id',
                    'name',
                    'insert_dt',
                    'update_dt'
                ]
                self.__checkBoxTableWidget.setHorizontalHeaderLabels(columns)
                self.__checkBoxTableWidget.setRowCount(len(self.__data))
                for i, d in enumerate(self.__data):
                    self.__checkBoxTableWidget.setItem(i, 1, QTableWidgetItem(d['id']))
                    self.__checkBoxTableWidget.setItem(i, 2, QTableWidgetItem(d['name']))
                    self.__checkBoxTableWidget.setItem(i, 3, QTableWidgetItem(d['insert_dt']))
                    self.__checkBoxTableWidget.setItem(i, 4, QTableWidgetItem(d['update_dt']))
            elif self.__import_type == 'chatgpt':
                result_dict = get_chatgpt_data_for_preview(path, most_recent_n)
                columns = result_dict['columns']
                self.__data = result_dict['data']
                self.__checkBoxTableWidget.setHorizontalHeaderLabels(columns)
                self.__checkBoxTableWidget.setRowCount(len(self.__data))

                for r_idx, r in enumerate(self.__data):
                    for c_idx, c in enumerate(columns):
                        v = r[c]
                        self.__checkBoxTableWidget.setItem(r_idx, c_idx + 1, QTableWidgetItem(str(v)))
                if THREAD_ORDERBY in columns:
                    self.__checkBoxTableWidget.sortByColumn(columns.index(THREAD_ORDERBY) + 1,
                                                            Qt.SortOrder.DescendingOrder)

            self.__checkBoxTableWidget.resizeColumnsToContents()
            self.__dataGrpBox.setEnabled(True)
            self.__allCheckBox.setChecked(True)
            self.__toggleBtn()
        except Exception as e:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], str(e))
            return

    def getData(self):
        checked_rows = self.__checkBoxTableWidget.getCheckedRows()
        if self.__import_type == 'general':
            self.__data = [self.__data[r] for r in checked_rows]
        elif self.__import_type == 'chatgpt':
            self.__data = get_chatgpt_data_for_import([self.__data[r] for r in checked_rows])
        return self.__data