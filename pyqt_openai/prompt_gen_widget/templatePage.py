from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QLabel, QSpacerItem, QListWidget, QListWidgetItem, QSizePolicy, QSplitter
from qtpy.QtWidgets import QWidget, QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, \
    QAbstractItemView

from pyqt_openai.prompt_gen_widget.promptGroupInputDialog import PromptGroupInputDialog
from pyqt_openai.prompt_gen_widget.templatePromptUnitInputDialog import TemplatePromptUnitInputDialog
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.widgets.button import Button


class TemplateGroupList(QWidget):
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

        self.__addBtn.setStyleAndIcon('ico/add.svg')
        self.__delBtn.setStyleAndIcon('ico/delete.svg')

        self.__addBtn.clicked.connect(self.__addGroup)
        self.__delBtn.clicked.connect(self.__deleteGroup)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Template Group']))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__templateList = QListWidget()

        defaultPropPromptGroupArr = DB.selectTemplatePromptGroup()
        if len(defaultPropPromptGroupArr) <= 0:
            self.__delBtn.setEnabled(False)

        for group in defaultPropPromptGroupArr:
            id = group[0]
            name = group[1]
            self.__addGroupItem(id, name)

        self.__templateList.currentRowChanged.connect(self.__currentRowChanged)
        self.__templateList.itemChanged.connect(self.__itemChanged)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__templateList)
        lay.setContentsMargins(0, 0, 5, 0)

        self.setLayout(lay)

        self.__templateList.setCurrentRow(0)

    def __addGroupItem(self, id, name):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(Qt.ItemDataRole.UserRole, id)
        item.setText(name)
        self.__templateList.addItem(item)
        self.__templateList.setCurrentItem(item)
        self.added.emit(id)

        self.__delBtn.setEnabled(True)

    def __addGroup(self):
        dialog = PromptGroupInputDialog(self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            name = dialog.getPromptGroupName()
            id = DB.insertTemplatePromptGroup({ 'name': name, 'data': [] })
            self.__addGroupItem(id, name)

    def __deleteGroup(self):
        i = self.__templateList.currentRow()
        item = self.__templateList.takeItem(i)
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.deleteTemplatePromptGroup(id)
        self.deleted.emit(id)

        defaultPropPromptGroupArr = DB.selectTemplatePromptGroup()
        if len(defaultPropPromptGroupArr) <= 0:
            self.__delBtn.setEnabled(False)

    def __itemChanged(self, item):
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.updateTemplatePromptGroup(id, item.text())
        self.itemChanged.emit(id)

    def __currentRowChanged(self, r_idx):
        item = self.__templateList.item(r_idx)
        if item:
            id = item.data(Qt.ItemDataRole.UserRole)
            self.currentRowChanged.emit(id)


class TemplateTable(QWidget):
    updated = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__title = ''
        self.__previousPromptTemplateArr = []

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__addBtn.setStyleAndIcon('ico/add.svg')
        self.__delBtn.setStyleAndIcon('ico/delete.svg')

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
        self.__table.setHorizontalHeaderLabels([LangClass.TRANSLATIONS['Act'], LangClass.TRANSLATIONS['Prompt']])
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.__table.currentItemChanged.connect(self.__rowChanged)
        self.__table.itemChanged.connect(self.__saveChangedTemplatePrompt)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__table)
        lay.setContentsMargins(5, 0, 0, 0)

        self.setLayout(lay)

        self.setNothingRightNow()

    def setTemplateArr(self, id):
        self.__id = id

        template_prompt_group = DB.selectTemplatePromptGroupId(self.__id)
        if template_prompt_group:
            self.__title = template_prompt_group[1]
        self.__previousPromptTemplateArr = DB.selectTemplatePromptUnit(self.__id)

        self.__titleLbl.setText(self.__title)

        self.__table.setRowCount(len(self.__previousPromptTemplateArr))
        for i in range(len(self.__previousPromptTemplateArr)):
            name = self.__previousPromptTemplateArr[i][2]
            value = self.__previousPromptTemplateArr[i][3]

            item1 = QTableWidgetItem(name)
            item1.setData(Qt.ItemDataRole.UserRole, self.__previousPromptTemplateArr[i][0])
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
        return self.__id

    def __rowChanged(self, new_item: QTableWidgetItem, old_item: QTableWidgetItem):
        name = ''
        prompt = ''
        # to avoid AttributeError
        if new_item:
            name_item = self.__table.item(new_item.row(), 0)
            name = name_item.text()
            prompt = self.__table.item(new_item.row(), 1).text() if new_item.column() == 0 else new_item.text()
        self.updated.emit(prompt, name)

    def __saveChangedTemplatePrompt(self, item: QTableWidgetItem):
        name_item = self.__table.item(item.row(), 0)
        id = name_item.data(Qt.ItemDataRole.UserRole)
        name = name_item.text()

        prompt_item = self.__table.item(item.row(), 1)
        prompt = prompt_item.text() if prompt_item else ''
        DB.updateTemplatePromptUnit(self.__id, id, name, prompt)
        
    def __add(self):
        dialog = TemplatePromptUnitInputDialog(self.__id, self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self.__table.itemChanged.disconnect(self.__saveChangedTemplatePrompt)

            name = dialog.getPromptName()
            self.__table.setRowCount(self.__table.rowCount()+1)

            item1 = QTableWidgetItem(name)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 0, item1)

            item2 = QTableWidgetItem('')
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 1, item2)

            id = DB.insertTemplatePromptUnit(self.__id, name)
            item1.setData(Qt.ItemDataRole.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedTemplatePrompt)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__table.selectedIndexes()]), reverse=True):
            id = self.__table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            self.__table.removeRow(i)
            DB.deleteTemplatePromptUnit(self.__id, id)

    def clearContents(self):
        self.__table.clearContents()


class TemplatePage(QWidget):
    updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        leftWidget = TemplateGroupList()
        leftWidget.added.connect(self.__templateGroupAdded)
        leftWidget.deleted.connect(self.__templateGroupDeleted)
        leftWidget.currentRowChanged.connect(self.__showTemplate)
        leftWidget.itemChanged.connect(self.__templateGroupUpdated)

        self.__templateGroupInit()

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__templateTable)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def __templateGroupInit(self):
        self.__templateTable = TemplateTable()
        self.__templateTable.updated.connect(self.updated)

    def __templateGroupAdded(self, id):
        self.__templateTable.setTemplateArr(id)

    def __templateGroupUpdated(self, id):
        self.__templateTable.setTemplateArr(id)

    def __templateGroupDeleted(self, id):
        if self.__templateTable.getId() == id:
            self.__templateTable.setNothingRightNow()
        elif len(DB.selectTemplatePromptGroup()) == 0:
            self.__templateTable.setNothingRightNow()

    def __showTemplate(self, id):
        self.__templateTable.setTemplateArr(id)