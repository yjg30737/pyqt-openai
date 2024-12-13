"""This dialog is for exporting conversation threads selected by the user from the history."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QLabel, QTableWidgetItem, QVBoxLayout

from pyqt_openai import THREAD_ORDERBY
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.checkBoxTableWidget import CheckBoxTableWidget

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class ExportDialog(QDialog):
    def __init__(
        self,
        columns: list[str],
        data: list[dict[str, Any]],
        sort_by: str = THREAD_ORDERBY,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initVal(columns, data, sort_by)
        self.__initUi()

    def __initVal(
        self,
        columns: list[str],
        data: list[dict[str, Any]],
        sort_by: str,
    ):
        self.__columns = columns
        self.__data = data
        self.__sort_by = sort_by

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Export"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__checkBoxTableWidget: CheckBoxTableWidget = CheckBoxTableWidget()
        self.__checkBoxTableWidget.setHorizontalHeaderLabels(self.__columns)
        self.__checkBoxTableWidget.setRowCount(len(self.__data))

        for r_idx, r in enumerate(self.__data):
            for c_idx, c in enumerate(self.__columns):
                v = r[c]
                self.__checkBoxTableWidget.setItem(
                    r_idx, c_idx + 1, QTableWidgetItem(str(v)),
                )

        self.__checkBoxTableWidget.resizeColumnsToContents()
        self.__checkBoxTableWidget.setSortingEnabled(True)
        if self.__sort_by in self.__columns:
            self.__checkBoxTableWidget.sortByColumn(
                self.__columns.index(self.__sort_by) + 1, Qt.SortOrder.DescendingOrder,
            )

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        allCheckBox = QCheckBox(LangClass.TRANSLATIONS["Select All"])
        allCheckBox.stateChanged.connect(
            self.__checkBoxTableWidget.toggleState,
        )  # if allChkBox is checked, tablewidget checkboxes will also be checked

        lay = QVBoxLayout()
        lay.addWidget(
            QLabel(LangClass.TRANSLATIONS["Select the threads you want to export."]),
        )
        lay.addWidget(allCheckBox)
        lay.addWidget(self.__checkBoxTableWidget)
        lay.addWidget(buttonBox)
        self.setLayout(lay)

    def getSelectedIds(self) -> list[str]:
        ids = [
            self.__checkBoxTableWidget.item(r, 1).text()  # type: ignore[union-attr]
            for r in self.__checkBoxTableWidget.getCheckedRows()
        ]
        return ids

