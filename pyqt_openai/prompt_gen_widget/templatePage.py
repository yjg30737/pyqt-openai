from qtpy.QtWidgets import QLabel, QSpacerItem, QListWidget, QListWidgetItem, QSizePolicy, QStackedWidget, QSplitter
from qtpy.QtWidgets import QWidget, QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, QAbstractItemView
from qtpy.QtCore import Signal, Qt

from pyqt_openai.inputDialog import InputDialog
from pyqt_openai.prompt_gen_widget.promptGroupInputDialog import PromptGroupInputDialog
from pyqt_openai.prompt_gen_widget.templatePromptUnitInputDialog import TemplatePromptUnitInputDialog
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgButton import SvgButton


class TemplateGroupList(QWidget):
    added = Signal(int)
    deleted = Signal(int)
    currentRowChanged = Signal(int)

    def __init__(self, db: SqliteDatabase):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db

    def __initUi(self):
        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')

        self.__addBtn.clicked.connect(self.__addGroup)
        self.__delBtn.clicked.connect(self.__deleteGroup)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Template Group']))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__templateList = QListWidget()

        defaultPropPromptGroupArr = self.__db.selectTemplatePromptGroup()

        for group in defaultPropPromptGroupArr:
            id = group[0]
            name = group[1]
            self.__addGroupItem(id, name)

        self.__templateList.currentRowChanged.connect(self.currentRowChanged)
        self.__templateList.itemChanged.connect(self.__itemChanged)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__templateList)
        lay.setContentsMargins(0, 0, 5, 0)

        self.setLayout(lay)

        self.__templateList.setCurrentRow(0)

    def __addGroupItem(self, id, name):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(Qt.UserRole, id)
        item.setText(name)
        self.__templateList.addItem(item)
        self.__templateList.setCurrentItem(item)
        self.added.emit(id)

    def __addGroup(self):
        dialog = PromptGroupInputDialog(self.__db, self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            name = dialog.getPromptGroupName()
            id = self.__db.insertTemplatePromptGroup({ 'name': name, 'data': [] })
            self.__addGroupItem(id, name)

    def __deleteGroup(self):
        i = self.__templateList.currentRow()
        item = self.__templateList.takeItem(i)
        id = item.data(Qt.UserRole)
        self.__db.deleteTemplatePromptGroup(id)
        self.deleted.emit(i)

    def __itemChanged(self, item):
        id = item.data(Qt.UserRole)
        self.__db.updateTemplatePromptGroup(id, item.text())


class TemplateTable(QWidget):
    updated = Signal(str, str)

    def __init__(self, db: SqliteDatabase, id):
        super().__init__()
        self.__initVal(db, id)
        self.__initUi()

    def __initVal(self, db, id):
        self.__db = db
        self.__id = id

        self.__title = self.__db.selectTemplatePromptGroupId(self.__id)[1]
        self.__previousPromptTemplateArr = self.__db.selectTemplatePromptUnit(self.__id)

    def __initUi(self):
        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(self.__title))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__table = QTableWidget()
        self.__table.setColumnCount(2)
        self.__table.setRowCount(len(self.__previousPromptTemplateArr))
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.__table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__table.setHorizontalHeaderLabels([LangClass.TRANSLATIONS['Act'], LangClass.TRANSLATIONS['Prompt']])
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.__table.currentItemChanged.connect(self.__rowChanged)

        for i in range(len(self.__previousPromptTemplateArr)):
            name = self.__previousPromptTemplateArr[i][2]
            value = self.__previousPromptTemplateArr[i][3]

            item1 = QTableWidgetItem(name)
            item1.setData(Qt.UserRole, self.__previousPromptTemplateArr[i][0])
            item1.setTextAlignment(Qt.AlignCenter)

            item2 = QTableWidgetItem(value)
            item2.setTextAlignment(Qt.AlignCenter)

            self.__table.setItem(i, 0, item1)
            self.__table.setItem(i, 1, item2)

        self.__table.itemChanged.connect(self.__saveChangedTemplatePrompt)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__table)
        lay.setContentsMargins(5, 0, 0, 0)

        self.setLayout(lay)

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
        id = name_item.data(Qt.UserRole)
        name = name_item.text()
        prompt = self.__table.item(item.row(), 1).text()
        self.__db.updateTemplatePromptUnit(self.__id, id, name, prompt)
        
    def __add(self):
        dialog = TemplatePromptUnitInputDialog(self.__db, self.__id, self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            self.__table.itemChanged.disconnect(self.__saveChangedTemplatePrompt)

            name = dialog.getPromptName()
            self.__table.setRowCount(self.__table.rowCount()+1)

            item1 = QTableWidgetItem(name)
            item1.setTextAlignment(Qt.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 0, item1)

            item2 = QTableWidgetItem('')
            item2.setTextAlignment(Qt.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 1, item2)

            id = self.__db.insertTemplatePromptUnit(self.__id, name)
            item1.setData(Qt.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedTemplatePrompt)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__table.selectedIndexes()]), reverse=True):
            id = self.__table.item(i, 0).data(Qt.UserRole)
            self.__table.removeRow(i)
            self.__db.deleteTemplatePromptUnit(self.__id, id)


class TemplatePage(QWidget):
    updated = Signal(str)

    def __init__(self, db: SqliteDatabase):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db
        self.__previousTemplateGroups = self.__db.selectTemplatePromptGroup()

    def __initUi(self):
        leftWidget = TemplateGroupList(self.__db)
        leftWidget.added.connect(self.__templateGroupAdded)
        leftWidget.deleted.connect(self.__templateGroupDeleted)
        leftWidget.currentRowChanged.connect(self.__showTemplate)

        self.__rightWidget = QStackedWidget()

        for group in self.__previousTemplateGroups:
            templateTable = TemplateTable(self.__db, id=group[0])
            templateTable.updated.connect(self.updated)
            self.__rightWidget.addWidget(templateTable)

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__rightWidget)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def __templateGroupAdded(self, id):
        templateTable = TemplateTable(self.__db, id)
        templateTable.updated.connect(self.updated)
        self.__rightWidget.addWidget(templateTable)
        self.__rightWidget.setCurrentWidget(templateTable)

    def __templateGroupDeleted(self, n):
        w = self.__rightWidget.widget(n)
        self.__rightWidget.removeWidget(w)

    def __showTemplate(self, n):
        self.__rightWidget.setCurrentIndex(n)
        w = self.__rightWidget.currentWidget()