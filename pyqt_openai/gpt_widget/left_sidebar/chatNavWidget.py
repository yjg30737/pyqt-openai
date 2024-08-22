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
    onImport = Signal(list)
    onExport = Signal(list)
    onFavoriteClicked = Signal(bool)

    def __init__(self, columns, table_nm, parent=None):
        super().__init__(parent)
        self.__initVal(columns, table_nm)
        self.__initUi()

    def __initVal(self, columns, table_nm):
        self.__columns = columns
        self.__table_nm = table_nm

    def __initUi(self):
        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText(LangClass.TRANSLATIONS['History'])

        self.__addBtn = Button()
        self.__delBtn = Button()
        self.__importBtn = Button()
        self.__saveBtn = Button()
        self.__clearBtn = Button()
        self.__refreshBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__delBtn.setStyleAndIcon(ICON_DELETE)
        self.__importBtn.setStyleAndIcon(ICON_IMPORT)
        self.__saveBtn.setStyleAndIcon(ICON_SAVE)
        self.__clearBtn.setStyleAndIcon(ICON_CLOSE)
        self.__refreshBtn.setStyleAndIcon(ICON_REFRESH)

        self.__addBtn.setToolTip(LangClass.TRANSLATIONS['Add'])
        self.__delBtn.setToolTip(LangClass.TRANSLATIONS['Delete'])
        self.__importBtn.setToolTip(LangClass.TRANSLATIONS['Import'])
        self.__saveBtn.setToolTip(LangClass.TRANSLATIONS['Export'])
        self.__clearBtn.setToolTip(LangClass.TRANSLATIONS['Remove All'])
        self.__refreshBtn.setToolTip(LangClass.TRANSLATIONS['Refresh'])

        self.__addBtn.clicked.connect(self.add)
        self.__delBtn.clicked.connect(self.__delete)
        self.__importBtn.clicked.connect(self.__import)
        self.__saveBtn.clicked.connect(self.__export)
        self.__clearBtn.clicked.connect(self.__clear)
        self.__refreshBtn.clicked.connect(self.__refresh)

        lay = QHBoxLayout()
        lay.addWidget(imageGenerationHistoryLbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__clearBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__saveBtn)
        lay.addWidget(self.__refreshBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        menuSubWidget1 = QWidget()
        menuSubWidget1.setLayout(lay)

        self.__searchBar = SearchBar()
        self.__searchBar.setPlaceHolder(LangClass.TRANSLATIONS['Search...'])
        self.__searchBar.searched.connect(self.__search)

        self.__searchOptionCmbBox = QComboBox()
        self.__searchOptionCmbBox.addItems([LangClass.TRANSLATIONS['Title'], LangClass.TRANSLATIONS['Content']])
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
        idx = self.__columns.index(THREAD_ORDERBY)
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
        self.__tableView.resizeColumnsToContents()
        self.__tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.__tableView.clicked.connect(self.__clicked)
        self.__tableView.activated.connect(self.__clicked)

        self.__favoriteBtn = QPushButton(LangClass.TRANSLATIONS['Favorite List'])
        self.__favoriteBtn.setCheckable(True)
        self.__favoriteBtn.toggled.connect(self.__onFavoriteClicked)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__tableView)
        lay.addWidget(self.__favoriteBtn)
        self.setLayout(lay)

        self.refreshData()

    def add(self, called_from_parent=False):
        if called_from_parent:
            pass
        else:
            self.added.emit()
        self.__model.select()

    def __import(self):
        dialog = ImportDialog(parent=self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            import_type = dialog.getImportType()
            chatImportDialog = ChatImportDialog(import_type=import_type, parent=self)
            reply = chatImportDialog.exec()
            if reply == QDialog.Accepted:
                data = chatImportDialog.getData()
                self.onImport.emit(data)

    def __export(self):
        columns = ChatThreadContainer.get_keys()
        data = DB.selectAllThread()
        sort_by = THREAD_ORDERBY
        if len(data) > 0:
            dialog = ExportDialog(columns, data, sort_by=sort_by, parent=self)
            reply = dialog.exec()
            if reply == QDialog.Accepted:
                self.onExport.emit(dialog.getSelectedIds())
        else:
            QMessageBox.information(self, LangClass.TRANSLATIONS['Information'], LangClass.TRANSLATIONS['No data to export.'])

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
        # get the source index
        source_idx = self.__proxyModel.mapToSource(idx)
        # get the primary key value of the row
        cur_id = self.__model.record(source_idx.row()).value("id")
        clicked_thread = DB.selectThread(cur_id)
        # get the title
        title = clicked_thread['name']

        self.clicked.emit(cur_id, title)

    def __getSelectedIds(self):
        selected_idx_s = self.__tableView.selectedIndexes()
        ids = []
        for idx in selected_idx_s:
            ids.append(self.__model.data(self.__proxyModel.mapToSource(idx.siblingAtColumn(0)), role=Qt.ItemDataRole.DisplayRole))
        ids = list(set(ids))
        return ids

    def __delete(self):
        ids = self.__getSelectedIds()
        for _id in ids:
            DB.deleteThread(_id)
        self.__model.select()
        self.cleared.emit()

    def __clear(self):
        '''
        Clear all data in the table
        '''
        # Before clearing, confirm the action
        reply = QMessageBox.question(self, LangClass.TRANSLATIONS['Confirm'], LangClass.TRANSLATIONS['Are you sure to clear all data?'], QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            DB.deleteThread()
            self.__model.select()
            self.cleared.emit()

    def __refresh(self):
        self.__model.select()

    def __search(self, search_text):
        # title
        if self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS['Title']:
            self.refreshData(search_text)
        # content
        elif self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS['Content']:
            if search_text:
                threads = DB.selectAllContentOfThread(content_to_select=search_text)
                ids = [_[0] for _ in threads]
                self.__model.setQuery(QSqlQuery(f"SELECT {','.join(self.__columns)} FROM {self.__table_nm} "
                                                f"WHERE id IN ({','.join(map(str, ids))})"))
            else:
                self.refreshData()

    def isCurrentConvExists(self):
        return self.__model.rowCount() > 0 and self.__tableView.currentIndex()

    def setColumns(self, columns):
        self.__columns = columns
        self.__model.clear()
        self.__model.setTable(self.__table_nm)
        self.__model.setQuery(QSqlQuery(f"SELECT {','.join(self.__columns)} FROM {self.__table_nm}"))
        self.__model.select()

    def __onFavoriteClicked(self, f):
        self.onFavoriteClicked.emit(f)

    def activateFavoriteFromParent(self, f):
        self.__favoriteBtn.setChecked(f)