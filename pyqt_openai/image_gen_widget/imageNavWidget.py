from qtpy.QtCore import Signal, QSortFilterProxyModel, Qt, QByteArray
from qtpy.QtSql import QSqlTableModel, QSqlDatabase
from qtpy.QtWidgets import QWidget, QVBoxLayout, QStyledItemDelegate, QTableView, QAbstractItemView, QHBoxLayout, QMessageBox, QLabel

# for search feature
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.widgets.searchBar import SearchBar
from pyqt_openai.widgets.svgButton import SvgButton


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
    getContent = Signal(bytes)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        # Set up the database and table model (you'll need to configure this part based on your database)
        self.__imageDb = QSqlDatabase.addDatabase('QSQLITE')  # Replace with your database type
        self.__imageDb.setDatabaseName('conv.db')  # Replace with your database name
        self.__imageDb.open()

        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText('History')

        self.__searchBar = SearchBar()
        self.__searchBar.setPlaceHolder('Search...')
        self.__searchBar.searched.connect(self.__showResult)

        self.__deleteBtn = SvgButton()
        self.__deleteBtn.setIcon('ico/delete.svg')
        self.__deleteBtn.clicked.connect(self.__delete)
        self.__deleteBtn.setToolTip('Delete Certain Row')

        self.__clearBtn = SvgButton()
        self.__clearBtn.setIcon('ico/close.svg')
        self.__clearBtn.clicked.connect(self.__clear)
        self.__deleteBtn.setToolTip('Remove All')

        lay = QHBoxLayout()
        lay.addWidget(self.__searchBar)
        lay.addWidget(self.__deleteBtn)
        lay.addWidget(self.__clearBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)

        columnNames = ['ID', 'Prompt', 'n', 'Size', 'Quality', 'Data', 'Revised Prompt']

        self.__model = SqlTableModel(self)
        self.__model.setTable('image_tb')
        self.__model.beforeUpdate.connect(self.__updated)
        for i in range(len(columnNames)):
            self.__model.setHeaderData(i, Qt.Horizontal, columnNames[i])
        self.__model.select()
        # descending order by date
        self.__model.sort(7, Qt.DescendingOrder)

        # init the proxy model
        self.__proxyModel = FilterProxyModel()

        # set the table model as source model to make it enable to feature sort and filter function
        self.__proxyModel.setSourceModel(self.__model)

        # set up the view
        self.__tableView = QTableView()
        self.__tableView.setModel(self.__proxyModel)
        self.__tableView.setEditTriggers(QTableView.NoEditTriggers)
        self.__tableView.setSortingEnabled(True)

        # align to center
        delegate = AlignDelegate()
        for i in range(self.__model.columnCount()):
            self.__tableView.setItemDelegateForColumn(i, delegate)

        # set selection/resize policy
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__tableView.resizeColumnsToContents()
        self.__tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.__tableView.clicked.connect(self.__clicked)

        lay = QVBoxLayout()
        lay.addWidget(imageGenerationHistoryLbl)
        lay.addWidget(menuWidget)
        lay.addWidget(self.__tableView)
        self.setLayout(lay)

        # show default result (which means "show all")
        self.__showResult('')

    def __updated(self, i, r):
        # send updated signal
        self.__model.updated.emit(r.value('id'), r.value('name'))

    def refresh(self):
        self.__model.select()

    def __clicked(self, idx):
        row = idx.row()
        col = 5

        idx = self.__model.index(row, col)
        data = self.__model.data(idx, role=Qt.DisplayRole)
        if isinstance(data, str):
            QMessageBox.critical(self, 'Error', f'Image URL can\'t bee seen after v0.2.51, Now it is replaced with b64_json.')
        else:
            data = QByteArray(data).data()
            self.getContent.emit(data)

    def __showResult(self, text):
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self.__proxyModel.setFilterKeyColumn(-1)
        # regular expression can be used
        self.__proxyModel.setFilterRegularExpression(text)

    def __delete(self):
        idx_s = self.__tableView.selectedIndexes()
        for idx in idx_s:
            idx = idx.siblingAtColumn(0)
            id = self.__model.data(idx, role=Qt.DisplayRole)
            DB.removeImage(id)
        self.__model.select()

    def __clear(self):
        DB.removeImage()
        self.__model.select()

