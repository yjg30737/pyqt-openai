import json
import os

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QDialog,
    QListWidget,
    QListWidgetItem,
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
from pyqt_openai.util.common import open_directory, get_prompt_data, export_prompt
from pyqt_openai.widgets.button import Button


class PromptGroupList(QWidget):
    added = Signal(int)
    deleted = Signal(int)
    currentRowChanged = Signal(int)
    itemChanged = Signal(int)

    def __init__(self, prompt_type='form', parent=None):
        super().__init__(parent)
        self.__initVal(prompt_type)
        self.__initUi()

    def __initVal(self, prompt_type):
        self.prompt_type = prompt_type

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
        lay.addWidget(QLabel(LangClass.TRANSLATIONS[f"{self.prompt_type.capitalize()} Group"]))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__exportBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        groups = DB.selectPromptGroup(prompt_type=self.prompt_type)
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
            id = DB.insertPromptGroup(name, prompt_type=self.prompt_type)
            self.__addGroupItem(id, name)

    def __delete(self):
        i = self.list.currentRow()
        item = self.list.takeItem(i)
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.deletePromptGroup(id)
        self.deleted.emit(id)

        groups = DB.selectPromptGroup(prompt_type=self.prompt_type)
        if len(groups) <= 0:
            self.__delBtn.setEnabled(False)

    def __import(self):
        dialog = PromptGroupImportDialog(parent=self, prompt_type=self.prompt_type)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            # Get the data
            result = dialog.getSelected()
            # Save the data
            for group in result:
                id = DB.insertPromptGroup(group["name"], prompt_type=self.prompt_type)
                for entry in group["data"]:
                    DB.insertPromptEntry(id, entry["act"], entry["prompt"])
                name = group["name"]
                self.__addGroupItem(id, name)

    def __export(self):
        try:
            if self.prompt_type == 'form':
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
                    data = get_prompt_data(prompt_type=self.prompt_type)
                    dialog = PromptGroupExportDialog(data=data, parent=self)
                    reply = dialog.exec()
                    if reply == QDialog.DialogCode.Accepted:
                        data = dialog.getSelected()
                        # Save the data
                        with open(filename, "w") as f:
                            json.dump(data, f, indent=INDENT_SIZE)
            elif self.prompt_type == 'sentence':
                # Get the file
                file_data = QFileDialog.getSaveFileName(
                    self,
                    LangClass.TRANSLATIONS["Save"],
                    QFILEDIALOG_DEFAULT_DIRECTORY,
                    f"CSV files Compressed File (*.zip);;{JSON_FILE_EXT_LIST_STR}",
                )
                if file_data[0]:
                    filename = file_data[0]
                    # Get the data
                    data = get_prompt_data(self.prompt_type)
                    # Get extension
                    ext = os.path.splitext(filename)[1]
                    # If it is a compressed file, it is a compressed csv, so change the extension to csv
                    if ext == ".zip":
                        ext = ".csv"
                    dialog = PromptGroupExportDialog(data=data, ext=ext, parent=self)
                    reply = dialog.exec()
                    if reply == QDialog.DialogCode.Accepted:
                        data = dialog.getSelected()
                        export_prompt(data, filename, ext)
                        open_directory(os.path.dirname(filename))
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