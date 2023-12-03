from PyQt5.QtSql import QSqlDatabase
from qtpy.QtCore import Signal, QSortFilterProxyModel, Qt
from qtpy.QtSql import QSqlTableModel
from qtpy.QtWidgets import QWidget, QVBoxLayout, QStyledItemDelegate, QApplication, QTableView, QAbstractItemView


# for search feature
from pyqt_openai.searchBar import SearchBar


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
        option.displayAlignment = Qt.AlignCenter


class SqlTableModel(QSqlTableModel):
    added = Signal(int, str)
    updated = Signal(int, str)
    deleted = Signal(list)
    addedCol = Signal()
    deletedCol = Signal()

    def flags(self, index) -> Qt.ItemFlags:
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return super().flags(index)


class ImageNavWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        # Set up the database and table model (you'll need to configure this part based on your database)
        self.__imageDb = QSqlDatabase.addDatabase('QSQLITE')  # Replace with your database type
        self.__imageDb.setDatabaseName('conv.db')  # Replace with your database name
        self.__imageDb.open()

        searchBar = SearchBar()
        columnNames = ['ID', 'Prompt', 'n', 'Size', 'Quality', 'URL']

        self.__model = SqlTableModel(self)
        self.__model.setTable('image_tb')
        self.__model.beforeUpdate.connect(self.__updated)
        for i in range(len(columnNames)):
            self.__model.setHeaderData(i, Qt.Horizontal, columnNames[i])
        self.__model.select()

        # init the proxy model
        self.__proxyModel = FilterProxyModel()

        # set the table model as source model to make it enable to feature sort and filter function
        self.__proxyModel.setSourceModel(self.__model)

        # set up the view
        self.__tableView = QTableView()
        self.__tableView.setModel(self.__proxyModel)
        self.__tableView.setEditTriggers(QTableView.NoEditTriggers)

        # align to center
        delegate = AlignDelegate()
        for i in range(self.__model.columnCount()):
            self.__tableView.setItemDelegateForColumn(i, delegate)

        # set selection/resize policy
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__tableView.resizeColumnsToContents()
        self.__tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # sort (ascending order by default)
        self.__tableView.setSortingEnabled(True)
        self.__tableView.sortByColumn(0, Qt.AscendingOrder)

        # set current index as first record
        self.__tableView.setCurrentIndex(self.__tableView.model().index(0, 0))

        lay = QVBoxLayout()
        lay.addWidget(searchBar)
        lay.addWidget(self.__tableView)
        self.setLayout(lay)

    def __updated(self, i, r):
        # send updated signal
        self.__model.updated.emit(r.value('id'), r.value('name'))

    def refresh(self):
        self.__model.select()