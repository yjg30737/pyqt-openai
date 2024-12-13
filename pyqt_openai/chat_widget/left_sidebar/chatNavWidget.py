from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import QSortFilterProxyModel, Qt, Signal
from qtpy.QtSql import QSqlQuery, QSqlTableModel
from qtpy.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from pyqt_openai import ICON_ADD, ICON_IMPORT, ICON_REFRESH, ICON_SAVE, THREAD_ORDERBY
from pyqt_openai.chat_widget.left_sidebar.exportDialog import ExportDialog
from pyqt_openai.chat_widget.left_sidebar.importDialog import ImportDialog
from pyqt_openai.chat_widget.left_sidebar.selectChatImportTypeDialog import SelectChatImportTypeDialog
from pyqt_openai.globals import DB
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ChatThreadContainer
from pyqt_openai.widgets.baseNavWidget import BaseNavWidget
from pyqt_openai.widgets.button import Button

if TYPE_CHECKING:
    from qtpy.QtCore import QModelIndex, QPersistentModelIndex
    from qtpy.QtWidgets import QStyleOptionViewItem


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.__searchedText: str = ""

    @property
    def searchedText(self) -> str:
        return self.__searchedText

    @searchedText.setter
    def searchedText(self, value):
        self.__searchedText = value
        self.invalidateFilter()


# for align text in every cell to center
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter


class SqlTableModel(QSqlTableModel):
    added = Signal(int, str)
    updated = Signal(int, str)
    deleted = Signal(list)
    addedCol = Signal()
    deletedCol = Signal()

    def flags(
        self,
        index: QModelIndex | QPersistentModelIndex,
    ) -> Qt.ItemFlag:
        if index.column() == self.column_index_by_name("name"):
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEditable
            )
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def column_index_by_name(self, name: str) -> int:
        return self.fieldIndex(name)


class ChatNavWidget(BaseNavWidget):
    added: Signal = Signal()
    clicked: Signal = Signal(int, str)
    cleared: Signal = Signal()
    onImport: Signal = Signal(list)
    onExport: Signal = Signal(list)
    onFavoriteClicked: Signal = Signal(bool)

    def __init__(
        self,
        columns: list[str],
        table_nm: str,
        parent: QWidget | None = None,
    ):
        super().__init__(columns, table_nm, parent)
        self.__initUi()

    def __initUi(self):
        self.setModel(table_type="chat")

        imageGenerationHistoryLbl = QLabel()
        imageGenerationHistoryLbl.setText(LangClass.TRANSLATIONS["History"])

        self.__addBtn = Button()
        self.__importBtn = Button()
        self.__saveBtn = Button()
        self.__refreshBtn = Button()

        self.__addBtn.setStyleAndIcon(ICON_ADD)
        self.__importBtn.setStyleAndIcon(ICON_IMPORT)
        self.__saveBtn.setStyleAndIcon(ICON_SAVE)
        self.__refreshBtn.setStyleAndIcon(ICON_REFRESH)

        self.__addBtn.setToolTip(LangClass.TRANSLATIONS["Add"])
        self.__importBtn.setToolTip(LangClass.TRANSLATIONS["Import"])
        self.__saveBtn.setToolTip(LangClass.TRANSLATIONS["Export"])
        self.__refreshBtn.setToolTip(LangClass.TRANSLATIONS["Refresh"])

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
        self.__searchOptionCmbBox.addItems(
            [LangClass.TRANSLATIONS["Title"], LangClass.TRANSLATIONS["Content"]],
        )
        self.__searchOptionCmbBox.setMinimumHeight(self._searchBar.sizeHint().height())
        self.__searchOptionCmbBox.currentIndexChanged.connect(
            lambda _: self._search(self._searchBar.getSearchBar().text()),
        )

        hlay = QHBoxLayout()
        hlay.addWidget(self._searchBar)
        hlay.addWidget(self.__searchOptionCmbBox)
        hlay.setContentsMargins(0, 0, 0, 0)

        menuSubWidget2 = QWidget()
        menuSubWidget2.setLayout(hlay)

        vlay1 = QVBoxLayout()
        vlay1.addWidget(menuSubWidget1)
        vlay1.addWidget(menuSubWidget2)
        vlay1.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(vlay1)

        self._tableView.clicked.connect(self.__clicked)
        self._tableView.activated.connect(self.__clicked)

        self.__favoriteBtn = QPushButton(LangClass.TRANSLATIONS["Favorite List"])
        self.__favoriteBtn.setCheckable(True)
        self.__favoriteBtn.toggled.connect(self.__onFavoriteClicked)

        vlay2 = QVBoxLayout()
        vlay2.addWidget(menuWidget)
        vlay2.addWidget(self._tableView)
        vlay2.addWidget(self.__favoriteBtn)
        self.setLayout(vlay2)

        self.refreshData()

    def add(self, called_from_parent=False):
        if called_from_parent:
            pass
        else:
            self.added.emit()
        self._model.select()

    def __import(self):
        dialog = SelectChatImportTypeDialog(parent=self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            import_type = dialog.getImportType()
            chatImportDialog = ImportDialog(
                import_type=import_type,  # type: ignore[arg-type]
                parent=self,
            )
            reply = chatImportDialog.exec()
            if reply == QDialog.DialogCode.Accepted:
                data = chatImportDialog.getData()
                self.onImport.emit(data)

    def __export(self):
        columns = ChatThreadContainer.get_keys()
        data = DB.selectAllThread()
        sort_by = THREAD_ORDERBY
        if len(data) > 0:
            dialog = ExportDialog(columns, data, sort_by=sort_by, parent=self)
            reply = dialog.exec()
            if reply == QDialog.DialogCode.Accepted:
                self.onExport.emit(dialog.getSelectedIds())
        else:
            QMessageBox.information(
                self,
                LangClass.TRANSLATIONS["Information"],
                LangClass.TRANSLATIONS["No data to export."],
            )

    def refreshData(
        self,
        title: str | None = None,
    ):
        self._model.select()
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self._proxyModel.setFilterKeyColumn(-1)
        # regular expression can be used
        self._proxyModel.setFilterRegularExpression(title or "")

    def __clicked(self, idx: QModelIndex | QPersistentModelIndex):
        # get the source index
        source_idx = self._proxyModel.mapToSource(idx)
        # get the primary key value of the row
        cur_id = self._model.record(source_idx.row()).value("id")
        clicked_thread = DB.selectThread(cur_id)
        # get the title
        title = clicked_thread["name"]

        self.clicked.emit(cur_id, title)

    def __getSelectedIds(self) -> list[int]:
        selected_idx_s = self._tableView.selectedIndexes()
        ids = []
        for idx in selected_idx_s:
            ids.append(
                self._model.data(
                    self._proxyModel.mapToSource(idx.siblingAtColumn(0)),
                    role=Qt.ItemDataRole.DisplayRole,
                ),
            )
        ids = list(set(ids))
        return ids

    # TODO LANGUAGE
    def _delete(self):
        reply = QMessageBox.question(  # type: ignore[call-arg]
            self,
            LangClass.TRANSLATIONS["Confirm"],
            LangClass.TRANSLATIONS["Are you sure to delete the selected data?"],
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ids = self.__getSelectedIds()
            for _id in ids:
                DB.deleteThread(_id)
            self._model.select()
            self.cleared.emit()

    def _clear(
        self,
        table_type: str = "chat",
    ):
        table_type = table_type or "chat"
        super()._clear(table_type=table_type)
        self.cleared.emit()

    def __refresh(self):
        self._model.select()

    def _search(self, text: str):
        # title
        if self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS["Title"]:
            self.refreshData(text)
        # content
        elif (
            self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS["Content"]
        ):
            if text:
                threads = DB.selectAllContentOfThread(content_to_select=text)
                ids = [_[0] for _ in threads]
                self._model.setQuery(
                    QSqlQuery(
                        f"SELECT {','.join(self._columns)} FROM {self._table_nm} "
                        f"WHERE id IN ({','.join(map(str, ids))})",
                    ),
                )
            else:
                self.refreshData()

    def isCurrentConvExists(self) -> QModelIndex | None:
        return self._model.rowCount() > 0 and self._tableView.currentIndex() or None

    def setColumns(
        self,
        columns: list[str],
        table_type: str = "chat",
    ):
        super().setColumns(columns, table_type=table_type)

    def __onFavoriteClicked(self, f: bool):
        self.onFavoriteClicked.emit(f)

    def activateFavoriteFromParent(self, f: bool):
        self.__favoriteBtn.setChecked(f)
