"""
This dialog is for exporting conversation threads selected by the user from the history.
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTableWidgetItem, QLabel, QDialogButtonBox, QCheckBox, QDialog, QVBoxLayout

from pyqt_openai.constants import THREAD_ORDERBY
from pyqt_openai.widgets.checkBoxTableWidget import CheckBoxTableWidget


class ExportDialog(QDialog):
    def __init__(self, columns, data, sort_by=THREAD_ORDERBY, parent=None):
        super(ExportDialog, self).__init__(parent)
        self.__initVal(columns, data, sort_by)
        self.__initUi()

    def __initVal(self, columns, data, sort_by):
        self.__columns = columns
        self.__data = data
        self.__sort_by = sort_by

    def __initUi(self):
        self.setWindowTitle("Export")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__checkBoxTableWidget = CheckBoxTableWidget()
        self.__checkBoxTableWidget.setHorizontalHeaderLabels(self.__columns)
        self.__checkBoxTableWidget.setRowCount(len(self.__data))

        for r_idx, r in enumerate(self.__data):
            for c_idx, c in enumerate(self.__columns):
                v = r[c]
                self.__checkBoxTableWidget.setItem(r_idx, c_idx+1, QTableWidgetItem(str(v)))

        self.__checkBoxTableWidget.resizeColumnsToContents()
        self.__checkBoxTableWidget.setSortingEnabled(True)
        if self.__sort_by in self.__columns:
            self.__checkBoxTableWidget.sortByColumn(self.__columns.index(self.__sort_by)+1, Qt.SortOrder.DescendingOrder)

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        allCheckBox = QCheckBox('Select All')
        allCheckBox.stateChanged.connect(self.__checkBoxTableWidget.toggleState) # if allChkBox is checked, tablewidget checkboxes will also be checked

        lay = QVBoxLayout()
        lay.addWidget(QLabel('Select the threads you want to export.'))
        lay.addWidget(allCheckBox)
        lay.addWidget(self.__checkBoxTableWidget)
        lay.addWidget(buttonBox)
        self.setLayout(lay)

    def getSelectedIds(self):
        ids = [self.__checkBoxTableWidget.item(r, 1).text() for r in self.__checkBoxTableWidget.getCheckedRows()]
        return ids
