from PySide6.QtCore import Signal, QSortFilterProxyModel, Qt, QByteArray
from PySide6.QtSql import QSqlTableModel, QSqlQuery
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStyledItemDelegate, QTableView, QAbstractItemView, QHBoxLayout, \
    QMessageBox, QLabel

from pyqt_openai import ICON_DELETE, ICON_CLOSE
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.widgets.baseNavWidget import BaseNavWidget
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


class ImageNavWidget(BaseNavWidget):
    getContent = Signal(bytes)

    def __init__(self, columns, table_nm, parent=None):
        super().__init__(columns, table_nm, parent)
        self.__initUi()

    def __initUi(self):
        self.setModel(table_type='image')

        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText(LangClass.TRANSLATIONS['History'])

        lay = QHBoxLayout()
        lay.addWidget(self._searchBar)
        lay.addWidget(self._delBtn)
        lay.addWidget(self._clearBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)

        self._tableView.activated.connect(self.__clicked)
        self._tableView.clicked.connect(self.__clicked)

        lay = QVBoxLayout()
        lay.addWidget(imageGenerationHistoryLbl)
        lay.addWidget(menuWidget)
        lay.addWidget(self._tableView)
        self.setLayout(lay)

        # Show default result (which means "show all")
        self._search('')

    def _clear(self, table_type='image'):
        table_type = table_type or 'image'
        super()._clear(table_type=table_type)

    def refresh(self):
        self._model.select()

    def __clicked(self, idx):
        # get the source index
        source_idx = self._proxyModel.mapToSource(idx)

        # get the primary key value of the row
        cur_id = self._model.record(source_idx.row()).value("id")

        # Get data from DB id
        data = DB.selectCertainImage(cur_id)['data']
        if data:
            if isinstance(data, str):
                QMessageBox.critical(self, LangClass.TRANSLATIONS['Error'], LangClass.TRANSLATIONS['Image URL can\'t be seen after v0.2.51, Now it is replaced with b64_json.'])
            else:
                data = QByteArray(data).data()
                self.getContent.emit(data)
        else:
            QMessageBox.critical(self, LangClass.TRANSLATIONS['Error'], LangClass.TRANSLATIONS['No image data is found. Maybe you are using really old version.'])

    def _search(self, text):
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self._proxyModel.setFilterKeyColumn(-1)
        # regular expression can be used
        self._proxyModel.setFilterRegularExpression(text)

    def _delete(self):
        idx_s = self._tableView.selectedIndexes()
        for idx in idx_s:
            idx = idx.siblingAtColumn(0)
            id = self._model.data(idx, role=Qt.ItemDataRole.DisplayRole)
            DB.removeImage(id)
        self._model.select()

    def setColumns(self, columns, table_type='image'):
        super().setColumns(columns, table_type='image')
