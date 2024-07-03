from qtpy.QtCore import Signal, QSortFilterProxyModel, Qt
from qtpy.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox, QStyledItemDelegate, QTableView, QAbstractItemView, \
    QHBoxLayout, \
    QLabel, QSpacerItem, QSizePolicy, QFileDialog, QComboBox

# for search feature
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.searchBar import SearchBar


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.__searchedText = ''

    @property
    def searchedText(self):
        return self.__searchedText

    @searchedText.setter
    def searchedText(self, value):
        self.__searchedText = value
        self.invalidateFilter()


# for align text in every cell to center
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter


class SqlTableModel(QSqlTableModel):
    added = Signal(int, str)
    updated = Signal(int, str)
    deleted = Signal(list)
    addedCol = Signal()
    deletedCol = Signal()

    def flags(self, index):
        if index.column() == self.column_index_by_name('name'):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def column_index_by_name(self, name):
        return self.fieldIndex(name)


class ChatNavWidget(QWidget):
    added = Signal()
    clicked = Signal(int, str)
    cleared = Signal()
    onImport = Signal(str)
    onExport = Signal(list)

    def __init__(self, columns, table_nm):
        super().__init__()
        self.__initVal(columns, table_nm)
        self.__initUi()

    def __initVal(self, columns, table_nm):
        self.__columns = columns
        self.__table_nm = table_nm

    def __initUi(self):
        # Set up the database and table model (you'll need to configure this part based on your database)
        self.__imageDb = QSqlDatabase.addDatabase('QSQLITE')  # Replace with your database type
        self.__imageDb.setDatabaseName('conv.db')  # Replace with your database name
        self.__imageDb.open()

        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText('History')

        self.__addBtn = Button()
        self.__delBtn = Button()
        self.__importBtn = Button()
        self.__saveBtn = Button()
        self.__clearBtn = Button()

        self.__addBtn.setStyleAndIcon('ico/add.svg')
        self.__delBtn.setStyleAndIcon('ico/delete.svg')
        self.__importBtn.setStyleAndIcon('ico/import.svg')
        self.__saveBtn.setStyleAndIcon('ico/save.svg')
        self.__clearBtn.setStyleAndIcon('ico/close.svg')

        self.__addBtn.setToolTip('Add')
        self.__delBtn.setToolTip('Delete')
        self.__importBtn.setToolTip('SQLite DB Import (Working)')
        self.__saveBtn.setToolTip('Save')
        self.__delBtn.setToolTip('Remove All')

        self.__addBtn.clicked.connect(self.add)
        self.__delBtn.clicked.connect(self.__delete)
        self.__importBtn.clicked.connect(self.__import)
        self.__saveBtn.clicked.connect(self.__export)
        self.__clearBtn.clicked.connect(self.__clear)

        lay = QHBoxLayout()
        lay.addWidget(imageGenerationHistoryLbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__clearBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__saveBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        menuSubWidget1 = QWidget()
        menuSubWidget1.setLayout(lay)

        self.__searchBar = SearchBar()
        self.__searchBar.setPlaceHolder('Search...')
        self.__searchBar.searched.connect(self.__search)

        self.__searchOptionCmbBox = QComboBox()
        self.__searchOptionCmbBox.addItems(['Title', 'Content'])
        self.__searchOptionCmbBox.setMinimumHeight(self.__searchBar.sizeHint().height())
        self.__searchOptionCmbBox.currentIndexChanged.connect(
            lambda _: self.__search(self.__searchBar.getSearchBar().text()))

        lay = QHBoxLayout()
        lay.addWidget(self.__searchBar)
        lay.addWidget(self.__searchOptionCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        menuSubWidget2 = QWidget()
        menuSubWidget2.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(menuSubWidget1)
        lay.addWidget(menuSubWidget2)
        lay.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)

        self.__model = SqlTableModel(self)
        self.__model.setTable(self.__table_nm)
        self.__model.beforeUpdate.connect(self.__updated)

        for i in range(len(self.__columns)):
            self.__model.setHeaderData(i, Qt.Orientation.Horizontal, self.__columns[i])
        self.__model.select()
        # descending order by insert date
        idx = self.__columns.index('insert_dt')
        self.__model.sort(idx, Qt.SortOrder.DescendingOrder)

        # init the proxy model
        self.__proxyModel = FilterProxyModel()

        # set the table model as source model to make it enable to feature sort and filter function
        self.__proxyModel.setSourceModel(self.__model)

        # set up the view
        self.__tableView = QTableView()
        self.__tableView.setModel(self.__proxyModel)
        self.__tableView.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.SelectedClicked)
        self.__tableView.setSortingEnabled(True)

        # align to center
        delegate = AlignDelegate()
        for i in range(self.__model.columnCount()):
            self.__tableView.setItemDelegateForColumn(i, delegate)

        # set selection/resize policy
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.__tableView.clicked.connect(self.__clicked)
        self.__tableView.activated.connect(self.__clicked)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__tableView)
        self.setLayout(lay)

        self.refreshData()

    def add(self, called_from_parent=False):
        if called_from_parent:
            pass
        else:
            self.added.emit()
        self.__model.select()

    def __import(self):
        filename = QFileDialog.getOpenFileName(self, 'Import', '', 'SQLite DB files (*.db)')
        if filename:
            filename = filename[0]
            self.onImport.emit(filename)

    def __export(self):
        self.onExport.emit(self.__getSelectedIds())

    def __updated(self, i, r):
        # send updated signal
        self.__model.updated.emit(r.value('id'), r.value('name'))

    def refreshData(self, title=None):
        self.__model.select()
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self.__proxyModel.setFilterKeyColumn(-1)
        # regular expression can be used
        self.__proxyModel.setFilterRegularExpression(title)

    def __clicked(self, idx):
        # get id of record
        id = self.__model.data(self.__proxyModel.mapToSource(idx.siblingAtColumn(0)), role=Qt.ItemDataRole.DisplayRole)
        title = self.__model.data(self.__proxyModel.mapToSource(idx.siblingAtColumn(1)), role=Qt.ItemDataRole.DisplayRole)

        self.clicked.emit(id, title)

    def __getSelectedIds(self):
        idx_s = [idx.siblingAtColumn(0) for idx in self.__tableView.selectedIndexes()]
        idx_s = list(set(idx_s))
        ids = [self.__model.data(idx, role=Qt.ItemDataRole.DisplayRole) for idx in idx_s]
        return ids

    def __delete(self):
        ids = self.__getSelectedIds()
        for _id in ids:
            DB.deleteConv(_id)
        self.__model.select()
        self.cleared.emit()

    def __clear(self):
        '''
        Clear all data in the table
        '''
        # Before clearing, confirm the action
        reply = QMessageBox.question(self, 'Confirm', 'Are you sure to clear all data?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            DB.deleteConv()
            self.__model.select()
            self.cleared.emit()

    def __search(self, search_text):
        # title
        if self.__searchOptionCmbBox.currentText() == 'Title':
            self.refreshData(search_text)
        # content
        elif self.__searchOptionCmbBox.currentText() == 'Content':
            if search_text:
                convs = DB.selectAllContentOfConv(content_to_select=search_text)
                ids = [_[0] for _ in convs]
                self.__model.setQuery(QSqlQuery(f"SELECT {','.join(self.__columns)} FROM {self.__table_nm} "
                                                f"WHERE id IN ({','.join(map(str, ids))})"))
            else:
                self.refreshData()

    def isCurrentConvExists(self):
        return self.__model.rowCount() > 0 and self.__tableView.currentIndex()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ChatNavWidget(['id', 'name', 'update_dt', 'insert_dt'], 'conv_tb')
    w.show()
    sys.exit(app.exec())