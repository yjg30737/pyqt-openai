from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QMessageBox, QGroupBox, QLabel, QDialogButtonBox, QCheckBox, QDialog, QVBoxLayout, QSpinBox

from pyqt_openai import JSON_FILE_EXT
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import get_chatgpt_data, get_conversation
from pyqt_openai.widgets.checkBoxTableWidget import CheckBoxTableWidget
from pyqt_openai.widgets.findPathWidget import FindPathWidget


class GeneralImportDialog(QDialog):
    def __init__(self):
        super(GeneralImportDialog, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # Data to be imported
        self.__data = []

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Import"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        findPathWidget = FindPathWidget()
        findPathWidget.added.connect(self.__setPath)
        findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS['Select a json file to import'])
        findPathWidget.setExtOfFiles(JSON_FILE_EXT)

        self.__mostRecentNSpinBox = QSpinBox()
        self.__mostRecentNSpinBox.setRange(1, 10000)
        self.__mostRecentNSpinBox.setEnabled(False)

        self.__checkBoxTableWidget = CheckBoxTableWidget()
        self.__checkBoxTableWidget.setColumnCount(0)

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
        self.__buttonBox.accepted.connect(self.__accept)
        self.__buttonBox.rejected.connect(self.reject)
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        lay = QVBoxLayout()
        lay.addWidget(findPathWidget)
        lay.addWidget(self.__dataGrpBox)
        lay.addWidget(self.__buttonBox)

        self.setLayout(lay)

        self.resize(800, 600)

    def __setData(self):
        checked_rows = self.__checkBoxTableWidget.getCheckedRows()
        self.__data = get_chatgpt_data([self.__data[r] for r in checked_rows])

    def __toggleOkButton(self):
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.__checkBoxTableWidget.getCheckedRows()) > 0)

    def __setPath(self, path):
        try:
            data = get_conversation(path)
            print(data)
            # columns = result_dict['columns']
            # self.__data = result_dict['data']
            # self.__checkBoxTableWidget.setHorizontalHeaderLabels(columns)
            # self.__checkBoxTableWidget.setRowCount(len(self.__data))
            #
            # for r_idx, r in enumerate(self.__data):
            #     for c_idx, c in enumerate(columns):
            #         v = r[c]
            #         self.__checkBoxTableWidget.setItem(r_idx, c_idx+1, QTableWidgetItem(str(v)))
            #
            # self.__checkBoxTableWidget.resizeColumnsToContents()
            # self.__checkBoxTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            # if THREAD_ORDERBY in columns:
            #     self.__checkBoxTableWidget.sortByColumn(columns.index(THREAD_ORDERBY)+1, Qt.SortOrder.DescendingOrder)
            # self.__chatGPTDataGroupBox.setEnabled(True)
            # self.__allCheckBox.setChecked(True)
            # self.__toggleOkButton()
            #
            # self.__checkBoxTableWidget.hideColumn(1)
        except Exception as e:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], LangClass.TRANSLATIONS['Check whether the file is a valid JSON file for importing.'])

    def __accept(self):
        if len(self.__checkBoxTableWidget.getCheckedRows()) > 0:
            self.__setData()
            self.accept()
        else:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], LangClass.TRANSLATIONS['Select at least one thread to import.'])

    def getData(self):
        return self.__data



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = GeneralImportDialog()
    w.show()
    sys.exit(app.exec())