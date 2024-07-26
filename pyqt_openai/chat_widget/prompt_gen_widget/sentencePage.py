import json
import os

from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QWidget, QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QFileDialog, QLabel, QSpacerItem, QListWidget, QListWidgetItem, QSizePolicy, QSplitter, QMessageBox

from pyqt_openai import JSON_FILE_EXT, ICON_ADD, ICON_DELETE, ICON_IMPORT, ICON_EXPORT
from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupDirectInputDialog import PromptGroupDirectInputDialog
from pyqt_openai.chat_widget.prompt_gen_widget.promptEntryDirectInputDialog import PromptEntryDirectInputDialog
from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupExportDialog import PromptGroupExportDialog
from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupImportDialog import PromptGroupImportDialog
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import open_directory
from pyqt_openai.widgets.button import Button


class SentenceGroupList(QWidget):
    added = Signal(int)
    deleted = Signal(int)
    currentRowChanged = Signal(int)
    itemChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__delBtn.setStyleAndIcon(ICON_DELETE)

        self.__importBtn = Button()
        self.__importBtn.setStyleAndIcon(ICON_IMPORT)
        self.__importBtn.setToolTip(LangClass.TRANSLATIONS['Import'])

        self.__exportBtn = Button()
        self.__exportBtn.setStyleAndIcon(ICON_EXPORT)
        self.__exportBtn.setToolTip(LangClass.TRANSLATIONS['Export'])

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)
        self.__importBtn.clicked.connect(self.__import)
        self.__exportBtn.clicked.connect(self.__export)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Sentence Group']))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__exportBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__list = QListWidget()

        groups = DB.selectPromptGroup(prompt_type='sentence')
        if len(groups) <= 0:
            self.__delBtn.setEnabled(False)

        for group in groups:
            id = group.id
            name = group.name
            self.__addGroupItem(id, name)

        self.__list.currentRowChanged.connect(self.__currentRowChanged)
        self.__list.itemChanged.connect(self.__itemChanged)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__list)
        lay.setContentsMargins(0, 0, 5, 0)

        self.setLayout(lay)

        self.__list.setCurrentRow(0)

    def __addGroupItem(self, id, name):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(Qt.ItemDataRole.UserRole, id)
        item.setText(name)
        self.__list.addItem(item)
        self.__list.setCurrentItem(item)
        self.added.emit(id)

        self.__delBtn.setEnabled(True)

    def __add(self):
        dialog = PromptGroupDirectInputDialog(self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            name = dialog.getPromptGroupName()
            id = DB.insertPromptGroup(name, prompt_type='sentence')
            self.__addGroupItem(id, name)

    def __delete(self):
        i = self.__list.currentRow()
        item = self.__list.takeItem(i)
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.deletePromptGroup(id)
        self.deleted.emit(id)

        groups = DB.selectPromptGroup(prompt_type='sentence')
        if len(groups) <= 0:
            self.__delBtn.setEnabled(False)

    def __import(self):
        dialog = PromptGroupImportDialog()
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            # Get the data
            result = dialog.getSelected()
            # Save the data
            for group in result:
                id = DB.insertPromptGroup(group['name'], prompt_type='sentence')
                for entry in group['data']:
                    DB.insertPromptEntry(id, entry['name'], entry['content'])
                name = group['name']
                self.__addGroupItem(id, name)

    def __export(self):
        try:
            # Get the file
            file_data = QFileDialog.getSaveFileName(self, LangClass.TRANSLATIONS['Save'], os.path.expanduser('~'), JSON_FILE_EXT)
            if file_data[0]:
                filename = file_data[0]
                # Get the data
                data = []
                for group in DB.selectPromptGroup(prompt_type='sentence'):
                    group_obj = {
                        'name': group.name,
                        'data': []
                    }
                    for entry in DB.selectPromptEntry(group.id):
                        group_obj['data'].append({
                            'name': entry.name,
                            'content': entry.content
                        })
                    data.append(group_obj)
                dialog = PromptGroupExportDialog(data)
                reply = dialog.exec()
                if reply == QDialog.DialogCode.Accepted:
                    # Save the data
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=4)
                    open_directory(os.path.dirname(filename))
        except Exception as e:
            QMessageBox.critical(self, LangClass.TRANSLATIONS['Error'], str(e))
            print(e)

    def __itemChanged(self, item):
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.updatePromptGroup(id, item.text())
        self.itemChanged.emit(id)

    def __currentRowChanged(self, r_idx):
        item = self.__list.item(r_idx)
        if item:
            id = item.data(Qt.ItemDataRole.UserRole)
            self.currentRowChanged.emit(id)


class PromptTable(QWidget):
    updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__title = ''
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
        self.__table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__table.setHorizontalHeaderLabels([LangClass.TRANSLATIONS['Name'], LangClass.TRANSLATIONS['Value']])
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.__table.currentItemChanged.connect(self.__rowChanged)
        self.__table.itemChanged.connect(self.__saveChangedPrompt)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__table)
        lay.setContentsMargins(5, 0, 0, 0)

        self.setLayout(lay)

        self.setNothingRightNow()

    def showEntries(self, id):
        self.__group_id = id

        prompt_group = DB.selectCertainPromptGroup(id=self.__group_id)
        if prompt_group and isinstance(prompt_group, list) and len(prompt_group) > 0:
            self.__title = prompt_group[0].name
        self.__entries = DB.selectPromptEntry(self.__group_id)

        self.__titleLbl.setText(self.__title)

        self.__table.setRowCount(len(self.__entries))
        for i in range(len(self.__entries)):
            name = self.__entries[i].name
            value = self.__entries[i].content

            item1 = QTableWidgetItem(name)
            item1.setData(Qt.ItemDataRole.UserRole, self.__entries[i].id)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item2 = QTableWidgetItem(value)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.__table.setItem(i, 0, item1)
            self.__table.setItem(i, 1, item2)

        self.__addBtn.setEnabled(True)
        self.__delBtn.setEnabled(True)

    def setNothingRightNow(self):
        self.__title = ''
        self.__titleLbl.setText(self.__title)
        self.__table.clearContents()
        self.__addBtn.setEnabled(False)
        self.__delBtn.setEnabled(False)

    def getId(self):
        return self.__group_id

    def __rowChanged(self, new_item: QTableWidgetItem, old_item: QTableWidgetItem):
        prompt = ''
        # To avoid AttributeError
        if new_item:
            prompt = self.__table.item(new_item.row(), 1).text() if new_item.column() == 0 else new_item.text()
        self.updated.emit(prompt)

    def __saveChangedPrompt(self, item: QTableWidgetItem):
        name_item = self.__table.item(item.row(), 0)
        id = name_item.data(Qt.ItemDataRole.UserRole)
        name = name_item.text()

        prompt_item = self.__table.item(item.row(), 1)
        prompt = prompt_item.text() if prompt_item else ''
        DB.updatePromptEntry(id, name, prompt)
        
    def __add(self):
        dialog = PromptEntryDirectInputDialog(self.__group_id)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self.__table.itemChanged.disconnect(self.__saveChangedPrompt)

            name = dialog.getPromptName()
            self.__table.setRowCount(self.__table.rowCount()+1)

            item1 = QTableWidgetItem(name)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 0, item1)

            item2 = QTableWidgetItem('')
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 1, item2)

            id = DB.insertPromptEntry(self.__group_id, name)
            item1.setData(Qt.ItemDataRole.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedPrompt)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__table.selectedIndexes()]), reverse=True):
            id = self.__table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            self.__table.removeRow(i)
            DB.deletePromptEntry(self.__group_id, id)

    def clearContents(self):
        self.__table.clearContents()


class SentencePage(QWidget):
    updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        leftWidget = SentenceGroupList()
        leftWidget.added.connect(self.add)
        leftWidget.deleted.connect(self.delete)
        leftWidget.currentRowChanged.connect(self.__showEntries)
        leftWidget.itemChanged.connect(self.__itemChanged)

        self.__table = PromptTable()
        self.__table.updated.connect(self.updated)

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__table)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def __itemChanged(self, id):
        self.__table.showEntries(id)

    def __showEntries(self, id):
        self.__table.showEntries(id)

    def add(self, id):
        self.__table.showEntries(id)

    def delete(self, id):
        if self.__table.getId() == id:
            self.__table.setNothingRightNow()
        elif len(DB.selectPromptGroup(prompt_type='sentence')) == 0:
            self.__table.setNothingRightNow()
