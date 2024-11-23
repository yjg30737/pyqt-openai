import json
import os

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QTableWidget,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QLabel,
    QAbstractItemView,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QSplitter,
)

from pyqt_openai import (
    JSON_FILE_EXT_LIST_STR,
    ICON_ADD,
    ICON_DELETE,
    ICON_IMPORT,
    ICON_EXPORT,
    QFILEDIALOG_DEFAULT_DIRECTORY,
    INDENT_SIZE,
)
from pyqt_openai.chat_widget.prompt_gen_widget.promptEntryDirectInputDialog import (
    PromptEntryDirectInputDialog,
)
from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupDirectInputDialog import (
    PromptGroupDirectInputDialog,
)
from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupExportDialog import (
    PromptGroupExportDialog,
)
from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupImportDialog import (
    PromptGroupImportDialog,
)
from pyqt_openai.globals import DB
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.common import open_directory, get_prompt_data
from pyqt_openai.widgets.button import Button


class FormGroupList(QWidget):
    added = Signal(int)
    deleted = Signal(int)
    currentRowChanged = Signal(int)
    itemChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__importBtn = Button()
        self.__importBtn.setToolTip(LangClass.TRANSLATIONS["Import"])

        self.__exportBtn = Button()
        self.__exportBtn.setToolTip(LangClass.TRANSLATIONS["Export"])

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__delBtn.setStyleAndIcon(ICON_DELETE)
        self.__importBtn.setStyleAndIcon(ICON_IMPORT)
        self.__exportBtn.setStyleAndIcon(ICON_EXPORT)

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)
        self.__importBtn.clicked.connect(self.__import)
        self.__exportBtn.clicked.connect(self.__export)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Form Group"]))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__exportBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        groups = DB.selectPromptGroup(prompt_type="form")
        if len(groups) <= 0:
            self.__delBtn.setEnabled(False)

        self.list = QListWidget()

        for group in groups:
            id = group.id
            name = group.name
            self.__addGroupItem(id, name)

        self.list.currentRowChanged.connect(self.__currentRowChanged)
        self.list.itemChanged.connect(self.__itemChanged)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.list)
        lay.setContentsMargins(0, 0, 5, 0)

        self.setLayout(lay)

    def __addGroupItem(self, id, name):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(Qt.ItemDataRole.UserRole, id)
        item.setText(name)
        self.list.addItem(item)
        self.list.setCurrentItem(item)
        self.added.emit(id)

        self.__delBtn.setEnabled(True)

    def __add(self):
        dialog = PromptGroupDirectInputDialog(self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            name = dialog.getPromptGroupName()
            id = DB.insertPromptGroup(name, prompt_type="form")
            self.__addGroupItem(id, name)

    def __delete(self):
        i = self.list.currentRow()
        item = self.list.takeItem(i)
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.deletePromptGroup(id)
        self.deleted.emit(id)

        groups = DB.selectPromptGroup(prompt_type="form")
        if len(groups) <= 0:
            self.__delBtn.setEnabled(False)

    def __import(self):
        dialog = PromptGroupImportDialog(parent=self, prompt_type="form")
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            # Get the data
            result = dialog.getSelected()
            # Save the data
            for group in result:
                id = DB.insertPromptGroup(group["name"], prompt_type="form")
                for entry in group["data"]:
                    DB.insertPromptEntry(id, entry["act"], entry["prompt"])
                name = group["name"]
                self.__addGroupItem(id, name)

    def __export(self):
        try:
            # Get the file
            file_data = QFileDialog.getSaveFileName(
                self,
                LangClass.TRANSLATIONS["Save"],
                QFILEDIALOG_DEFAULT_DIRECTORY,
                JSON_FILE_EXT_LIST_STR,
            )
            if file_data[0]:
                filename = file_data[0]
                # Get the data
                data = get_prompt_data(prompt_type="form")
                dialog = PromptGroupExportDialog(data=data, parent=self)
                reply = dialog.exec()
                if reply == QDialog.DialogCode.Accepted:
                    data = dialog.getSelected()
                    # Save the data
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=INDENT_SIZE)
                    open_directory(os.path.dirname(filename))
        except Exception as e:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], str(e))
            print(e)

    def __itemChanged(self, item):
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.updatePromptGroup(id, item.text())
        self.itemChanged.emit(id)

    def __currentRowChanged(self, r_idx):
        item = self.list.item(r_idx)
        if item:
            id = item.data(Qt.ItemDataRole.UserRole)
            self.currentRowChanged.emit(id)


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
        self.__table.setRowCount(len(self.__entries))
        self.__table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.__table.setHorizontalHeaderLabels(
            [LangClass.TRANSLATIONS["Name"], LangClass.TRANSLATIONS["Value"]]
        )
        self.__table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.__table.currentItemChanged.connect(self.__rowChanged)
        self.__table.itemChanged.connect(self.__saveChangedPrompt)

        # for i in range(len(self.__entries)):
        #     act = self.__entries[i].act
        #     prompt = self.__entries[i].prompt
        #
        #     item1 = QTableWidgetItem(act)
        #     item1.setData(Qt.ItemDataRole.UserRole, self.__entries[i].id)
        #     item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        #
        #     item2 = QTableWidgetItem(prompt)
        #     item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        #
        #     self.__table.setItem(i, 0, item1)
        #     self.__table.setItem(i, 1, item2)
        #
        # self.__table.itemChanged.connect(self.__generatePrompt)
        # self.__table.itemChanged.connect(self.__saveChangedPrompt)

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

    def getPromptText(self):
        prompt_text = ""
        for i in range(self.__table.rowCount()):
            name = self.__table.item(i, 0).text() if self.__table.item(i, 0) else ""
            value = self.__table.item(i, 1).text() if self.__table.item(i, 1) else ""
            if value.strip():
                prompt_text += f"{name}: {value}\n"
        return prompt_text

    def __generatePrompt(self):
        prompt_text = self.getPromptText()
        self.updated.emit(prompt_text)

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

            item2 = QTableWidgetItem("")
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount() - 1, 1, item2)

            id = DB.insertPromptEntry(self.__group_id, act, "")
            item1.setData(Qt.ItemDataRole.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedPrompt)

    def __delete(self):
        for i in sorted(
            set([i.row() for i in self.__table.selectedIndexes()]), reverse=True
        ):
            id = self.__table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            self.__table.removeRow(i)
            DB.deletePromptEntry(self.__group_id, id)


class FormPage(QWidget):
    updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__groups = DB.selectPromptGroup(prompt_type="form")

    def __initUi(self):
        leftWidget = FormGroupList()
        leftWidget.added.connect(self.add)
        leftWidget.deleted.connect(self.delete)

        leftWidget.currentRowChanged.connect(self.__showEntries)

        self.__table = PromptTable()
        if len(self.__groups) > 0:
            leftWidget.list.setCurrentRow(0)
            self.__table.showEntries(self.__groups[0].id)
        self.__table.updated.connect(self.updated)

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__table)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def add(self, id):
        self.__table.showEntries(id)

    def delete(self, id):
        if self.__table.getId() == id:
            self.__table.setNothingRightNow()
        elif len(DB.selectPromptGroup(prompt_type="form")) == 0:
            self.__table.setNothingRightNow()

    def __showEntries(self, id):
        self.__table.showEntries(id)
