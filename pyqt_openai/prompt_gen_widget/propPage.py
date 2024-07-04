from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QTableWidget, QSizePolicy, QSpacerItem, QStackedWidget, QLabel, \
    QAbstractItemView, QTableWidgetItem, QHeaderView, QHBoxLayout, \
    QVBoxLayout, QWidget, QDialog, QListWidget, QListWidgetItem, QSplitter

from pyqt_openai.prompt_gen_widget.promptGroupInputDialog import PromptGroupInputDialog
from pyqt_openai.prompt_gen_widget.propPromptUnitInputDialog import PropPromptUnitInputDialog
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.widgets.button import Button


class PropGroupList(QWidget):
    added = Signal(int)
    deleted = Signal(int)
    currentRowChanged = Signal(int)

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
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Property Group']))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        defaultPropPromptGroupArr = DB.selectPropPromptGroup()

        self.__propList = QListWidget()

        # TODO abcd
        for group in defaultPropPromptGroupArr:
            id = group[0]
            name = group[1]
            self.__addGroupItem(id, name)

        self.__propList.currentRowChanged.connect(self.currentRowChanged)
        self.__propList.itemChanged.connect(self.__itemChanged)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__propList)
        lay.setContentsMargins(0, 0, 5, 0)

        self.setLayout(lay)

        self.__propList.setCurrentRow(0)

    def __addGroupItem(self, id, name):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(Qt.ItemDataRole.UserRole, id)
        item.setText(name)
        self.__propList.addItem(item)
        self.__propList.setCurrentItem(item)
        self.added.emit(id)

    def __addGroup(self):
        dialog = PromptGroupInputDialog(self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            name = dialog.getPromptGroupName()
            id = DB.insertPropPromptGroup(name)
            self.__addGroupItem(id, name)

    def __deleteGroup(self):
        i = self.__propList.currentRow()
        item = self.__propList.takeItem(i)
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.deletePropPromptGroup(id)
        self.deleted.emit(i)

    def __itemChanged(self, item):
        id = item.data(Qt.ItemDataRole.UserRole)
        DB.updatePropPromptGroup(id, item.text())


class PropTable(QWidget):
    """
    benchmarked https://gptforwork.com/tools/prompt-generator
    """
    updated = Signal(str)

    def __init__(self, id):
        super().__init__()
        self.__initVal(id)
        self.__initUi()

    def __initVal(self, id):
        self.__id = id

        self.__title = DB.selectPropPromptGroupId(self.__id)[1]
        self.__previousPromptPropArr = DB.selectPropPromptAttribute(self.__id)

    def __initUi(self):
        self.__addBtn = Button()
        self.__delBtn = Button()

        self.__addBtn.setStyleAndIcon('ico/add.svg')
        self.__delBtn.setStyleAndIcon('ico/delete.svg')

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
        self.__table.setRowCount(len(self.__previousPromptPropArr))
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.__table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__table.setHorizontalHeaderLabels([LangClass.TRANSLATIONS['Name'], LangClass.TRANSLATIONS['Value']])

        for i in range(len(self.__previousPromptPropArr)):
            name = self.__previousPromptPropArr[i][2]
            value = self.__previousPromptPropArr[i][3]

            item1 = QTableWidgetItem(name)
            item1.setData(Qt.ItemDataRole.UserRole, self.__previousPromptPropArr[i][0])
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item2 = QTableWidgetItem(value)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.__table.setItem(i, 0, item1)
            self.__table.setItem(i, 1, item2)

        self.__table.itemChanged.connect(self.__generatePropPrompt)
        self.__table.itemChanged.connect(self.__saveChangedPropPrompt)

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

    def __generatePropPrompt(self, item: QTableWidgetItem):
        prompt_text = self.getPromptText()
        self.updated.emit(prompt_text)

    def __saveChangedPropPrompt(self, item: QTableWidgetItem):
        name = self.__table.item(item.row(), 0)
        id = name.data(Qt.ItemDataRole.UserRole)
        name = name.text()
        value = self.__table.item(item.row(), 1).text()
        DB.updatePropPromptAttribute(self.__id, id, name, value)

    def __add(self):
        dialog = PropPromptUnitInputDialog(self.__id, self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self.__table.itemChanged.disconnect(self.__saveChangedPropPrompt)

            name = dialog.getPromptName()
            self.__table.setRowCount(self.__table.rowCount()+1)

            item1 = QTableWidgetItem(name)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 0, item1)

            item2 = QTableWidgetItem('')
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 1, item2)

            id = DB.insertPropPromptAttribute(self.__id, name)
            item1.setData(Qt.ItemDataRole.UserRole, id)

            self.__table.itemChanged.connect(self.__saveChangedPropPrompt)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__table.selectedIndexes()]), reverse=True):
            id = self.__table.item(i, 0).data(Qt.ItemDataRole.UserRole)
            self.__table.removeRow(i)
            DB.deletePropPromptAttribute(self.__id, id)


class PropPage(QWidget):
    updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__previousPropGroups = DB.selectPropPromptGroup()

    def __initUi(self):
        leftWidget = PropGroupList()
        leftWidget.added.connect(self.__propGroupAdded)
        leftWidget.deleted.connect(self.__propGroupDeleted)
        leftWidget.currentRowChanged.connect(self.__showProp)

        self.__rightWidget = QStackedWidget()

        for group in self.__previousPropGroups:
            propTable = PropTable(id=group[0])
            propTable.updated.connect(self.updated)
            self.__rightWidget.addWidget(propTable)

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__rightWidget)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def __propGroupAdded(self, id):
        propTable = PropTable(id)
        propTable.updated.connect(self.updated)
        self.__rightWidget.addWidget(propTable)
        self.__rightWidget.setCurrentWidget(propTable)

    def __propGroupDeleted(self, n):
        w = self.__rightWidget.widget(n)
        self.__rightWidget.removeWidget(w)

    def __showProp(self, n):
        self.__rightWidget.setCurrentIndex(n)
        w = self.__rightWidget.currentWidget()
        if w and isinstance(w, PropTable):
            self.updated.emit(w.getPromptText())
