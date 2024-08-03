import json, os

from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QFileDialog, QTableWidget, QMessageBox, QSizePolicy, QSpacerItem, QStackedWidget, QLabel, \
    QAbstractItemView, QTableWidgetItem, QHeaderView, QHBoxLayout, \
    QVBoxLayout, QWidget, QDialog, QListWidget, QListWidgetItem, QSplitter

from pyqt_openai import JSON_FILE_EXT_LIST_STR, ICON_ADD, ICON_DELETE, ICON_IMPORT, ICON_EXPORT, \
    QFILEDIALOG_DEFAULT_DIRECTORY
from pyqt_openai.gpt_widget.prompt_gen_widget.promptGroupDirectInputDialog import PromptGroupDirectInputDialog
from pyqt_openai.gpt_widget.prompt_gen_widget.promptEntryDirectInputDialog import PromptEntryDirectInputDialog
from pyqt_openai.gpt_widget.prompt_gen_widget.promptGroupExportDialog import PromptGroupExportDialog
from pyqt_openai.gpt_widget.prompt_gen_widget.promptGroupImportDialog import PromptGroupImportDialog
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.util.script import open_directory, get_prompt_data
from pyqt_openai.widgets.button import Button


class FormGroupList(QWidget):
    added = Signal(int)
    deleted = Signal(int)
    currentRowChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__delBtn.setStyleAndIcon(ICON_DELETE)

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        self.__importBtn = Button()
        self.__importBtn.setStyleAndIcon(ICON_IMPORT)
        self.__importBtn.setToolTip(LangClass.TRANSLATIONS['Import'])
        self.__importBtn.clicked.connect(self.__import)

        self.__exportBtn = Button()
        self.__exportBtn.setStyleAndIcon(ICON_EXPORT)
        self.__exportBtn.setToolTip(LangClass.TRANSLATIONS['Export'])
        self.__exportBtn.clicked.connect(self.__export)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Form Group']))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__exportBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        groups = DB.selectPromptGroup(prompt_type='form')

        self.__list = QListWidget()

        for group in groups:
            self.__addGroupItem(group.id, group.name)

        self.__list.currentRowChanged.connect(self.currentRowChanged)
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

    def __add(self):
        dialog = PromptGroupDirectInputDialog(self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            name = dialog.getPromptGroupName()
            id = DB.insertPromptGroup(name, prompt_type='form')
            self.__addGroupItem(id, name)

    def __delete(self):
        i = self.__list.currentRow()
        item = self.__list.takeItem(i)
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.deletePromptGroup(id)
        self.deleted.emit(i)

    def __import(self):
        dialog = PromptGroupImportDialog(parent=self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            # Get the data
            result = dialog.getSelected()
            # Save the data
            for group in result:
                id = DB.insertPromptGroup(group['name'], prompt_type='form')
                for entry in group['data']:
                    DB.insertPromptEntry(id, entry['name'], entry['content'])
                name = group['name']
                self.__addGroupItem(id, name)

    def __export(self):
        try:
            # Get the file
            file_data = QFileDialog.getSaveFileName(self, LangClass.TRANSLATIONS['Save'], QFILEDIALOG_DEFAULT_DIRECTORY, JSON_FILE_EXT_LIST_STR)
            if file_data[0]:
                filename = file_data[0]
                # Get the data
                data = get_prompt_data(prompt_type='form')
                dialog = PromptGroupExportDialog(data, self)
                reply = dialog.exec()
                if reply == QDialog.DialogCode.Accepted:
                    data = dialog.getSelected()
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


class PromptTable(QWidget):
    """
    benchmarked https://gptforwork.com/tools/prompt-generator
    """
    updated = Signal(str)

    def __init__(self, id):
        super().__init__()
        self.__initVal(id)
        self.__initUi()

    def __initVal(self, id):
        self.__group_id = id

        self.__title = DB.selectCertainPromptGroup(self.__group_id).name
        self.__entries = DB.selectPromptEntry(self.__group_id)

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__delBtn.setStyleAndIcon(ICON_DELETE)

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(self.__title))
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
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.__table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__table.setHorizontalHeaderLabels([LangClass.TRANSLATIONS['Name'], LangClass.TRANSLATIONS['Value']])

        for i in range(len(self.__entries)):
            name = self.__entries[i].name
            content = self.__entries[i].content

            item1 = QTableWidgetItem(name)
            item1.setData(Qt.ItemDataRole.UserRole, self.__entries[i].id)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item2 = QTableWidgetItem(content)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.__table.setItem(i, 0, item1)
            self.__table.setItem(i, 1, item2)

        self.__table.itemChanged.connect(self.__generatePrompt)
        self.__table.itemChanged.connect(self.__saveChangedPrompt)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__table)
        lay.setContentsMargins(5, 0, 0, 0)

        self.setLayout(lay)

    def getPromptText(self):
        prompt_text = ''
        for i in range(self.__table.rowCount()):
            name = self.__table.item(i, 0).text() if self.__table.item(i, 0) else ''
            value = self.__table.item(i, 1).text() if self.__table.item(i, 1) else ''
            if value.strip():
                prompt_text += f'{name}: {value}\n'
        return prompt_text

    def __generatePrompt(self):
        prompt_text = self.getPromptText()
        self.updated.emit(prompt_text)

    def __saveChangedPrompt(self, item: QTableWidgetItem):
        name = self.__table.item(item.row(), 0)
        id = name.data(Qt.ItemDataRole.UserRole)
        name = name.text()
        content = self.__table.item(item.row(), 1).text()
        DB.updatePromptEntry(id, name, content)

    def __add(self):
        dialog = PromptEntryDirectInputDialog(self.__group_id, self)
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

            id = DB.insertPromptEntry(self.__group_id, name, '')
            item1.setData(Qt.ItemDataRole.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedPrompt)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__table.selectedIndexes()]), reverse=True):
            id = self.__table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            self.__table.removeRow(i)
            DB.deletePromptEntry(self.__group_id, id)


class FormPage(QWidget):
    updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__groups = DB.selectPromptGroup(prompt_type='form')

    def __initUi(self):
        leftWidget = FormGroupList()
        leftWidget.added.connect(self.__added)
        leftWidget.deleted.connect(self.__deleted)
        leftWidget.currentRowChanged.connect(self.__showEntries)

        self.__rightWidget = QStackedWidget()

        for group in self.__groups:
            promptTable = PromptTable(id=group.id)
            promptTable.updated.connect(self.updated)
            self.__rightWidget.addWidget(promptTable)

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__rightWidget)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def __added(self, id):
        promptTable = PromptTable(id)
        promptTable.updated.connect(self.updated)
        self.__rightWidget.addWidget(promptTable)
        self.__rightWidget.setCurrentWidget(promptTable)

    def __deleted(self, n):
        w = self.__rightWidget.widget(n)
        self.__rightWidget.removeWidget(w)

    def __showEntries(self, n):
        self.__rightWidget.setCurrentIndex(n)
        w = self.__rightWidget.currentWidget()
        if w and isinstance(w, PromptTable):
            self.updated.emit(w.getPromptText())
