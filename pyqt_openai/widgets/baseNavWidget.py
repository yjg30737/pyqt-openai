from abc import ABCMeta, abstractmethod

from PySide6.QtCore import Signal, QSortFilterProxyModel, Qt
from PySide6.QtSql import QSqlTableModel, QSqlQuery
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QPushButton, QStyledItemDelegate, QTableView, \
    QAbstractItemView, \
    QHBoxLayout, \
    QLabel, QSpacerItem, QSizePolicy, QComboBox, QDialog

from pyqt_openai import THREAD_ORDERBY, ICON_ADD, ICON_DELETE, ICON_IMPORT, ICON_SAVE, ICON_CLOSE, \
    ICON_REFRESH
from pyqt_openai.gpt_widget.left_sidebar.chatImportDialog import ChatImportDialog
from pyqt_openai.gpt_widget.left_sidebar.exportDialog import ExportDialog
from pyqt_openai.gpt_widget.left_sidebar.importDialog import ImportDialog
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ChatThreadContainer
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

    def __init__(self, table_type='chat', parent=None):
        super().__init__(parent)
        self.__table_type = table_type
        self.__parent = parent

    def flags(self, index):
        if self.__table_type == 'chat':
            if index.column() == self.column_index_by_name('name'):
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        elif self.__table_type == 'image':
            if index.column() == 0:
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return super().flags(index)

    def column_index_by_name(self, name):
        return self.fieldIndex(name)


class BaseNavWidget(QWidget):

    def __init__(self, columns, table_nm, parent=None):
        super().__init__(parent)
        self.__initVal(columns, table_nm)
        self.__initUi()

    def __initVal(self, columns, table_nm):
        self._columns = columns
        self._table_nm = table_nm

    def __initUi(self):
        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText(LangClass.TRANSLATIONS['History'])

        self._searchBar = SearchBar()
        self._searchBar.setPlaceHolder(LangClass.TRANSLATIONS['Search...'])
        self._searchBar.searched.connect(self._search)

        self._delBtn = Button()
        self._delBtn.setStyleAndIcon(ICON_DELETE)
        self._delBtn.clicked.connect(self._delete)
        self._delBtn.setToolTip(LangClass.TRANSLATIONS['Delete Certain Row'])

        self._clearBtn = Button()
        self._clearBtn.setStyleAndIcon(ICON_CLOSE)
        self._clearBtn.clicked.connect(self._clear)
        self._clearBtn.setToolTip(LangClass.TRANSLATIONS['Remove All'])

    def setModel(self, table_type='chat'):
        self._model = SqlTableModel(table_type, self)
        self._model.setTable(self._table_nm)
        self._model.beforeUpdate.connect(self._updated)

        # Set the query to fetch columns in the defined order
        # Remove DATA for GUI performance
        if table_type == 'image':
            if self._columns.__contains__('data'):
                self._columns.remove('data')
            self._model.setQuery(QSqlQuery(f"SELECT {','.join(self._columns)} FROM {self._table_nm}"))

        for i in range(len(self._columns)):
            self._model.setHeaderData(i, Qt.Orientation.Horizontal, self._columns[i])
        self._model.select()
        # descending order by insert date
        idx = self._columns.index('insert_dt')
        self._model.sort(idx, Qt.SortOrder.DescendingOrder)

        # init the proxy model
        self._proxyModel = FilterProxyModel()

        # set the table model as source model to make it enable to feature sort and filter function
        self._proxyModel.setSourceModel(self._model)

        # set up the view
        self._tableView = QTableView()
        self._tableView.setModel(self._proxyModel)
        self._tableView.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.SelectedClicked)
        self._tableView.setSortingEnabled(True)

        # align to center
        delegate = AlignDelegate()
        for i in range(self._model.columnCount()):
            self._tableView.setItemDelegateForColumn(i, delegate)

        # set selection/resize policy
        self._tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tableView.resizeColumnsToContents()
        self._tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # self.__tableView.activated.connect(self.__clicked)
        # self.__tableView.clicked.connect(self.__clicked)

    def _updated(self, i, r):
        # Send updated signal
        self._model.updated.emit(r.value('id'), r.value('name'))

    def _delete(self):
        pass

    def _search(self, text):
        pass

    def _clear(self, table_type='chat'):
        '''
        Clear all data in the table
        '''
        # Before clearing, confirm the action
        reply = QMessageBox.question(self, LangClass.TRANSLATIONS['Confirm'],
                                     LangClass.TRANSLATIONS['Are you sure to clear all data?'],
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if table_type == 'chat':
                DB.deleteThread()
            elif table_type == 'image':
                DB.removeImage()
            self._model.select()

    def setColumns(self, columns, table_type='chat'):
        self._columns = columns
        self._model.clear()
        self._model.setTable(self._table_nm)
        if table_type == 'image':
            # Remove DATA for GUI performance
            if self._columns.__contains__('data'):
                self._columns.remove('data')
        self._model.setQuery(QSqlQuery(f"SELECT {','.join(self._columns)} FROM {self._table_nm}"))
        self._model.select()

