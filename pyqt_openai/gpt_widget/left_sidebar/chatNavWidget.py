from PySide6.QtCore import Signal, QSortFilterProxyModel, Qt
from PySide6.QtSql import QSqlTableModel, QSqlQuery
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QPushButton, QStyledItemDelegate, QHBoxLayout, \
    QLabel, QSpacerItem, QSizePolicy, QComboBox, QDialog

import pyqt_openai.globals
from pyqt_openai import THREAD_ORDERBY, ICON_ADD, ICON_IMPORT, ICON_SAVE, ICON_REFRESH
from pyqt_openai.gpt_widget.left_sidebar.chatImportDialog import ChatImportDialog
from pyqt_openai.gpt_widget.left_sidebar.exportDialog import ExportDialog
from pyqt_openai.gpt_widget.left_sidebar.importDialog import ImportDialog
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ChatThreadContainer
from pyqt_openai.globals import DB
from pyqt_openai.widgets.baseNavWidget import BaseNavWidget
from pyqt_openai.widgets.button import Button


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


class ChatNavWidget(BaseNavWidget):
    added = Signal()
    clicked = Signal(int, str)
    cleared = Signal()
    onImport = Signal(list)
    onExport = Signal(list)
    onFavoriteClicked = Signal(bool)

    def __init__(self, columns, table_nm, parent=None):
        super().__init__(columns, table_nm, parent)
        self.__initUi()

    def __initUi(self):
        self.setModel(table_type='chat')

        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText(LangClass.TRANSLATIONS['History'])

        self.__addBtn = Button()
        self.__importBtn = Button()
        self.__saveBtn = Button()
        self.__refreshBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__importBtn.setStyleAndIcon(ICON_IMPORT)
        self.__saveBtn.setStyleAndIcon(ICON_SAVE)
        self.__refreshBtn.setStyleAndIcon(ICON_REFRESH)

        self.__addBtn.setToolTip(LangClass.TRANSLATIONS['Add'])
        self.__importBtn.setToolTip(LangClass.TRANSLATIONS['Import'])
        self.__saveBtn.setToolTip(LangClass.TRANSLATIONS['Export'])
        self.__refreshBtn.setToolTip(LangClass.TRANSLATIONS['Refresh'])

        self.__addBtn.clicked.connect(self.add)
        self.__importBtn.clicked.connect(self.__import)
        self.__saveBtn.clicked.connect(self.__export)
        self.__refreshBtn.clicked.connect(self.__refresh)

        lay = QHBoxLayout()
        lay.addWidget(imageGenerationHistoryLbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self._delBtn)
        lay.addWidget(self._clearBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__saveBtn)
        lay.addWidget(self.__refreshBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        menuSubWidget1 = QWidget()
        menuSubWidget1.setLayout(lay)

        self.__searchOptionCmbBox = QComboBox()
        self.__searchOptionCmbBox.addItems([LangClass.TRANSLATIONS['Title'], LangClass.TRANSLATIONS['Content']])
        self.__searchOptionCmbBox.setMinimumHeight(self._searchBar.sizeHint().height())
        self.__searchOptionCmbBox.currentIndexChanged.connect(
            lambda _: self._search(self._searchBar.getSearchBar().text()))

        lay = QHBoxLayout()
        lay.addWidget(self._searchBar)
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

        self._tableView.clicked.connect(self.__clicked)
        self._tableView.activated.connect(self.__clicked)

        self.__favoriteBtn = QPushButton(LangClass.TRANSLATIONS['Favorite List'])
        self.__favoriteBtn.setCheckable(True)
        self.__favoriteBtn.toggled.connect(self.__onFavoriteClicked)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self._tableView)
        lay.addWidget(self.__favoriteBtn)
        self.setLayout(lay)

        self.refreshData()

    def add(self, called_from_parent=False):
        if called_from_parent:
            pass
        else:
            self.added.emit()
        self._model.select()

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

    def refreshData(self, title=None):
        self._model.select()
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self._proxyModel.setFilterKeyColumn(-1)
        # regular expression can be used
        self._proxyModel.setFilterRegularExpression(title)

    def __clicked(self, idx):
        # get the source index
        source_idx = self._proxyModel.mapToSource(idx)
        # get the primary key value of the row
        cur_id = self._model.record(source_idx.row()).value("id")
        clicked_thread = DB.selectThread(cur_id)
        # get the title
        title = clicked_thread['name']

        self.clicked.emit(cur_id, title)

    def __getSelectedIds(self):
        selected_idx_s = self._tableView.selectedIndexes()
        ids = []
        for idx in selected_idx_s:
            ids.append(self._model.data(self._proxyModel.mapToSource(idx.siblingAtColumn(0)), role=Qt.ItemDataRole.DisplayRole))
        ids = list(set(ids))
        return ids

    # TODO LANGUAGE
    def _delete(self):
        reply = QMessageBox.question(self, LangClass.TRANSLATIONS['Confirm'],
                                     LangClass.TRANSLATIONS['Are you sure to delete the selected data?'],
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            ids = self.__getSelectedIds()
            for _id in ids:
                DB.deleteThread(_id)
            self._model.select()
            self.cleared.emit()

    def _clear(self, table_type='chat'):
        table_type = table_type or 'chat'
        super()._clear(table_type=table_type)
        self.cleared.emit()

    def __refresh(self):
        self._model.select()

    def _search(self, text):
        # title
        if self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS['Title']:
            self.refreshData(text)
        # content
        elif self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS['Content']:
            if text:
                threads = DB.selectAllContentOfThread(content_to_select=text)
                ids = [_[0] for _ in threads]
                self._model.setQuery(QSqlQuery(f"SELECT {','.join(self._columns)} FROM {self._table_nm} "
                                                f"WHERE id IN ({','.join(map(str, ids))})"))
            else:
                self.refreshData()

    def isCurrentConvExists(self):
        return self._model.rowCount() > 0 and self._tableView.currentIndex()

    def setColumns(self, columns, table_type='chat'):
        super().setColumns(columns, table_type='chat')

    def __onFavoriteClicked(self, f):
        self.onFavoriteClicked.emit(f)

    def activateFavoriteFromParent(self, f):
        self.__favoriteBtn.setChecked(f)