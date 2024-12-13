from __future__ import annotations

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pyqt_openai import (
    ICON_ADD,
    ICON_DELETE,
)
from pyqt_openai.chat_widget.prompt_gen_widget.promptEntryDirectInputDialog import (
    PromptEntryDirectInputDialog,
)
from pyqt_openai.globals import DB
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.button import Button


class PromptTable(QWidget):
    updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__title = ""
        self.__entries = []

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__delBtn.setStyleAndIcon(ICON_DELETE)

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        self.__titleLbl = QLabel()

        lay = QHBoxLayout()
        lay.addWidget(self.__titleLbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__table = QTableWidget()
        self.__table.setColumnCount(2)
        self.__table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.__table.setHorizontalHeaderLabels(
            [LangClass.TRANSLATIONS["Name"], LangClass.TRANSLATIONS["Value"]],
        )
        self.__table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch,
        )
        self.__table.currentItemChanged.connect(self.__rowChanged)
        self.__table.itemChanged.connect(self.__saveChangedPrompt)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__table)
        lay.setContentsMargins(5, 0, 0, 0)

        self.setLayout(lay)

    def showEntries(self, id):
        self.__group_id = id

        prompt_group = DB.selectCertainPromptGroup(id=self.__group_id)
        self.__title = prompt_group.name
        self.__entries = DB.selectPromptEntry(self.__group_id)

        self.__titleLbl.setText(self.__title)

        self.__table.setRowCount(len(self.__entries))
        for i in range(len(self.__entries)):
            act = self.__entries[i].act
            prompt = self.__entries[i].prompt

            item1 = QTableWidgetItem(act)
            item1.setData(Qt.ItemDataRole.UserRole, self.__entries[i].id)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item2 = QTableWidgetItem(prompt)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.__table.setItem(i, 0, item1)
            self.__table.setItem(i, 1, item2)

        self.__addBtn.setEnabled(True)
        self.__delBtn.setEnabled(True)

    def setNothingRightNow(self):
        self.__title = ""
        self.__titleLbl.setText(self.__title)
        self.__table.clearContents()
        self.__addBtn.setEnabled(False)
        self.__delBtn.setEnabled(False)

    def getId(self):
        return self.__group_id

    def __rowChanged(self, new_item: QTableWidgetItem, old_item: QTableWidgetItem):
        prompt = ""
        # To avoid AttributeError
        if new_item:
            prompt = (
                self.__table.item(new_item.row(), 1).text()
                if new_item.column() == 0
                else new_item.text()
            )
        self.updated.emit(prompt)

    def __saveChangedPrompt(self, item: QTableWidgetItem):
        act = self.__table.item(item.row(), 0)
        id = act.data(Qt.ItemDataRole.UserRole)
        act = act.text()

        prompt = self.__table.item(item.row(), 1)
        prompt = prompt.text() if prompt else ""
        DB.updatePromptEntry(id, act, prompt)

    def __add(self):
        dialog = PromptEntryDirectInputDialog(self.__group_id, self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self.__table.itemChanged.disconnect(self.__saveChangedPrompt)

            act = dialog.getAct()
            self.__table.setRowCount(self.__table.rowCount() + 1)

            item1 = QTableWidgetItem(act)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount() - 1, 0, item1)

            prompt = dialog.getPrompt()

            item2 = QTableWidgetItem(prompt)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount() - 1, 1, item2)

            id = DB.insertPromptEntry(self.__group_id, act, prompt)
            item1.setData(Qt.ItemDataRole.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedPrompt)

    def __delete(self):
        for i in sorted(
            set([i.row() for i in self.__table.selectedIndexes()]), reverse=True,
        ):
            id = self.__table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            self.__table.removeRow(i)
            DB.deletePromptEntry(self.__group_id, id)
