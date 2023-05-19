from qtpy.QtWidgets import QWidget, QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, QAbstractItemView
from qtpy.QtCore import Signal, Qt

from pyqt_openai.inputDialog import InputDialog
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgButton import SvgButton


class TemplatePage(QWidget):
    updated = Signal(str, str)

    def __init__(self, db: SqliteDatabase):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db
        self.__previousTemplateArr = self.__db.selectTemplatePrompt()

    def __initUi(self):
        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        # this template has to be connected with db
        # QSqlTableModel
        self.__templateTable = QTableWidget()
        self.__templateTable.setColumnCount(2)
        self.__templateTable.setHorizontalHeaderLabels(['Name', 'Content'])
        self.__templateTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.__templateTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__templateTable.currentItemChanged.connect(self.__rowChanged)

        self.__templateTable.setRowCount(len(self.__previousTemplateArr))

        for i in range(len(self.__previousTemplateArr)):
            id = self.__previousTemplateArr[i][0]
            name = self.__previousTemplateArr[i][1]
            value = self.__previousTemplateArr[i][2]

            content_item = QTableWidgetItem(name)
            content_item.setTextAlignment(Qt.AlignCenter)
            content_item.setData(Qt.UserRole, id)

            self.__templateTable.setItem(i, 0, content_item)
            self.__templateTable.setItem(i, 1, QTableWidgetItem(value))

        self.__templateTable.itemChanged.connect(self.__saveUpdatedTemplate)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__templateTable)

        self.setLayout(lay)

    def __rowChanged(self, new_item: QTableWidgetItem, old_item: QTableWidgetItem):
        name_item = self.__templateTable.item(new_item.row(), 0)
        name = name_item.text()
        content = self.__templateTable.item(new_item.row(), 1).text() if new_item.column() == 0 else new_item.text()
        self.updated.emit(content, name)

    def __saveUpdatedTemplate(self, item: QTableWidgetItem):
        name_item = self.__templateTable.item(item.row(), 0)
        id = name_item.data(Qt.UserRole)
        name = name_item.text()
        content = self.__templateTable.item(item.row(), 1).text()
        self.__db.updateTemplatePrompt(id, name, content)

    def __add(self):
        dialog = InputDialog('Name', '', self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            self.__templateTable.itemChanged.disconnect(self.__saveUpdatedTemplate)

            text = dialog.getText()
            self.__templateTable.setRowCount(self.__templateTable.rowCount()+1)

            item1 = QTableWidgetItem(text)
            item1.setTextAlignment(Qt.AlignCenter)
            self.__templateTable.setItem(self.__templateTable.rowCount()-1, 0, item1)

            item2 = QTableWidgetItem('')
            item2.setTextAlignment(Qt.AlignCenter)
            self.__templateTable.setItem(self.__templateTable.rowCount()-1, 1, item2)

            id = self.__db.insertTemplatePrompt(text)
            item1.setData(Qt.UserRole, id)

            self.__templateTable.itemChanged.connect(self.__saveUpdatedTemplate)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__templateTable.selectedIndexes()]), reverse=True):
            id = self.__templateTable.item(i, 0).data(Qt.UserRole)
            self.__db.deleteTemplatePrompt(id)
            self.__templateTable.removeRow(i)