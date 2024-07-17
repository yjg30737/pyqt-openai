from qtpy.QtCore import Signal, QSortFilterProxyModel, Qt, QByteArray
from qtpy.QtSql import QSqlTableModel, QSqlQuery
from qtpy.QtWidgets import QWidget, QVBoxLayout, QStyledItemDelegate, QTableView, QAbstractItemView, QHBoxLayout, \
    QMessageBox, QLabel

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
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return super().flags(index)


class ImageNavWidget(QWidget):
    getContent = Signal(bytes)

    def __init__(self, columns, table_nm):
        super().__init__()
        self.__initVal(columns, table_nm)
        self.__initUi()

    def __initVal(self, columns, table_nm):
        self.__columns = columns
        self.__table_nm = table_nm

    def __initUi(self):
        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText('History')

        self.__searchBar = SearchBar()
        self.__searchBar.setPlaceHolder('Search...')
        self.__searchBar.searched.connect(self.__showResult)

        self.__delBtn = Button()
        self.__delBtn.setStyleAndIcon('ico/delete.svg')
        self.__delBtn.clicked.connect(self.__delete)
        self.__delBtn.setToolTip('Delete Certain Row')

        self.__clearBtn = Button()
        self.__clearBtn.setStyleAndIcon('ico/close.svg')
        self.__clearBtn.clicked.connect(self.__clear)
        self.__delBtn.setToolTip('Remove All')

        lay = QHBoxLayout()
        lay.addWidget(self.__searchBar)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__clearBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)

        self.__model = SqlTableModel(self)
        self.__model.setTable(self.__table_nm)
        self.__model.beforeUpdate.connect(self.__updated)

        # Set the query to fetch columns in the defined order
        # Remove DATA for GUI performance
        if self.__columns.__contains__('data'):
            self.__columns.remove('data')
        self.__model.setQuery(QSqlQuery(f"SELECT {','.join(self.__columns)} FROM {self.__table_nm}"))

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
        self.__tableView.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.__tableView.setSortingEnabled(True)

        # align to center
        delegate = AlignDelegate()
        for i in range(self.__model.columnCount()):
            self.__tableView.setItemDelegateForColumn(i, delegate)

        # set selection/resize policy
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__tableView.resizeColumnsToContents()
        self.__tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.__tableView.activated.connect(self.__clicked)
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
        # get the source index
        source_idx = self.__proxyModel.mapToSource(idx)

        # get the primary key value of the row
        cur_id = self.__model.record(source_idx.row()).value("id")

        # Get data from DB id
        data = DB.selectCertainImage(cur_id)['data']
        if data:
            if isinstance(data, str):
                QMessageBox.critical(self, 'Error', f'Image URL can\'t be seen after v0.2.51, Now it is replaced with b64_json.')
            else:
                data = QByteArray(data).data()
                self.getContent.emit(data)
        else:
            QMessageBox.critical(self, 'Error', 'No image data is found. Maybe you are using really old version.')

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
            id = self.__model.data(idx, role=Qt.ItemDataRole.DisplayRole)
            DB.removeImage(id)
        self.__model.select()

    def __clear(self):
        DB.removeImage()
        self.__model.select()

    def setColumns(self, columns):
        self.__columns = columns
        self.__model.clear()
        self.__model.setTable(self.__table_nm)
        self.__model.setQuery(QSqlQuery(f"SELECT {','.join(self.__columns)} FROM {self.__table_nm}"))
        self.__model.select()
