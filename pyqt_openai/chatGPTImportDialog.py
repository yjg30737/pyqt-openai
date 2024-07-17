from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMessageBox, QPushButton, QGroupBox, QTableWidgetItem, \
    QLabel, QDialogButtonBox, QCheckBox, QDialog, QVBoxLayout, QSpinBox, QAbstractItemView

from pyqt_openai.constants import THREAD_ORDERBY
from pyqt_openai.util.script import get_conversation_from_chatgpt, get_chatgpt_data
from pyqt_openai.widgets.checkBoxTableWidget import CheckBoxTableWidget
from pyqt_openai.widgets.findPathWidget import FindPathWidget


class ChatGPTImportDialog(QDialog):
    def __init__(self):
        super(ChatGPTImportDialog, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # Get the most recent n conversation threads
        self.__most_recent_n = 10
        # Data to be imported
        self.__data = []

    def __initUi(self):
        self.setWindowTitle("Import ChatGPT Data")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        findPathWidget = FindPathWidget()
        findPathWidget.added.connect(self.__setPath)
        findPathWidget.getLineEdit().setPlaceholderText('Select a ChatGPT JSON file')
        findPathWidget.setExtOfFiles('JSON Files (*.json)')

        self.__chkBoxMostRecent = QCheckBox('Get most recent')

        self.__mostRecentNSpinBox = QSpinBox()
        self.__mostRecentNSpinBox.setRange(1, 10000)
        self.__mostRecentNSpinBox.setValue(self.__most_recent_n)
        self.__mostRecentNSpinBox.setEnabled(False)

        self.__chkBoxMostRecent.stateChanged.connect(lambda state: self.__mostRecentNSpinBox.setEnabled(state == Qt.CheckState.Checked))

        chatGPTImportGrpBox = QGroupBox('ChatGPT Import Options')
        lay = QVBoxLayout()
        lay.addWidget(self.__chkBoxMostRecent)
        lay.addWidget(self.__mostRecentNSpinBox)
        chatGPTImportGrpBox.setLayout(lay)

        self.__checkBoxTableWidget = CheckBoxTableWidget()
        self.__checkBoxTableWidget.setColumnCount(0)
        # self.__checkBoxTableWidget.checkedSignal.connect(self.getData)

        self.__allCheckBox = QCheckBox('Select All')
        self.__allCheckBox.stateChanged.connect(self.__checkBoxTableWidget.toggleState) # if allChkBox is checked, tablewidget checkboxes will also be checked

        lay = QVBoxLayout()
        lay.addWidget(QLabel('Select the threads you want to import.'))
        lay.addWidget(self.__allCheckBox)
        lay.addWidget(self.__checkBoxTableWidget)

        self.__chatGPTDataGroupBox = QGroupBox('ChatGPT Data')
        self.__chatGPTDataGroupBox.setLayout(lay)
        self.__chatGPTDataGroupBox.setEnabled(False)

        self.__buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.__buttonBox.accepted.connect(self.__accept)
        self.__buttonBox.rejected.connect(self.reject)
        self.__buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        lay = QVBoxLayout()
        lay.addWidget(findPathWidget)
        lay.addWidget(chatGPTImportGrpBox)
        lay.addWidget(self.__chatGPTDataGroupBox)
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
            most_recent_n = self.__mostRecentNSpinBox.value() if self.__chkBoxMostRecent.isChecked() else None
            result_dict = get_conversation_from_chatgpt(path, most_recent_n)
            columns = result_dict['columns']
            self.__data = result_dict['data']
            self.__checkBoxTableWidget.setHorizontalHeaderLabels(columns)
            self.__checkBoxTableWidget.setRowCount(len(self.__data))

            for r_idx, r in enumerate(self.__data):
                for c_idx, c in enumerate(columns):
                    v = r[c]
                    self.__checkBoxTableWidget.setItem(r_idx, c_idx+1, QTableWidgetItem(str(v)))

            self.__checkBoxTableWidget.resizeColumnsToContents()
            self.__checkBoxTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            if THREAD_ORDERBY in columns:
                self.__checkBoxTableWidget.sortByColumn(columns.index(THREAD_ORDERBY)+1, Qt.SortOrder.DescendingOrder)
            self.__chatGPTDataGroupBox.setEnabled(True)
            self.__allCheckBox.setChecked(True)
            self.__toggleOkButton()

            self.__checkBoxTableWidget.hideColumn(1)
        except Exception as e:
            QMessageBox.critical(self, "Error", 'Check whether the file is a valid JSON file for importing.')

    def __accept(self):
        if len(self.__checkBoxTableWidget.getCheckedRows()) > 0:
            self.__setData()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", 'Select at least one thread to import.')

    def getData(self):
        return self.__data