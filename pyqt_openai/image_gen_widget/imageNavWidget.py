import os

from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QTableView, QAbstractItemView
from qtpy.QtCore import Signal, QSortFilterProxyModel, Qt
from qtpy.QtSvg import QSvgWidget
from qtpy.QtWidgets import QWidget, QVBoxLayout, QStyledItemDelegate, QHBoxLayout, QGridLayout, QLabel, QLineEdit, \
    QApplication


class SearchBar(QWidget):
    searched = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # search bar label
        self.__label = QLabel()

        self.__searchLineEdit = QLineEdit()
        self.__searchIcon = QSvgWidget()
        ps = QApplication.font().pointSize()
        self.__searchIcon.setFixedSize(ps, ps)

        self.__searchBar = QWidget()
        self.__searchBar.setObjectName('searchBar')

        lay = QHBoxLayout()
        lay.addWidget(self.__searchIcon)
        lay.addWidget(self.__searchLineEdit)
        self.__searchBar.setLayout(lay)
        lay.setContentsMargins(ps // 2, 0, 0, 0)
        lay.setSpacing(0)

        self.__searchLineEdit.setFocus()
        self.__searchLineEdit.textChanged.connect(self.__searched)

        self.setAutoFillBackground(True)

        lay = QHBoxLayout()
        lay.addWidget(self.__searchBar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        self._topWidget = QWidget()
        self._topWidget.setLayout(lay)

        lay = QGridLayout()
        lay.addWidget(self._topWidget)

        searchWidget = QWidget()
        searchWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        lay = QGridLayout()
        lay.addWidget(searchWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__setStyle()

        self.setLayout(lay)

    # ex) searchBar.setLabel(True, 'Search Text')
    def setLabel(self, visibility: bool = True, text=None):
        if text:
            self.__label.setText(text)
        self.__label.setVisible(visibility)

    def __setStyle(self):
        self.__searchIcon.load(os.path.join(os.path.dirname(__file__), 'search.svg'))
        # set style sheet
        self.__searchLineEdit.setStyleSheet('''
        QLineEdit
        {
            background: transparent;
            color: #333333;
            border: none;
        }
        ''')
        self.__searchBar.setStyleSheet('''
        QWidget#searchBar
        {
            border: 1px solid gray;
        }
        ''')
        self.setStyleSheet('QWidget { padding: 5px; }')

    def __searched(self, text):
        self.searched.emit(text)

    def setSearchIcon(self, icon_filename: str):
        self.__searchIcon.load(icon_filename)

    def setPlaceHolder(self, text: str):
        self.__searchLineEdit.setPlaceholderText(text)

    def getSearchBar(self):
        return self.__searchLineEdit

    def getSearchLabel(self):
        return self.__searchIcon

    def showEvent(self, e):
        self.__searchLineEdit.setFocus()


# for search feature
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
        searchBar = SearchBar()
        columnNames = ['Prompt', 'Size', 'Quality', 'URL']

        self.__model = SqlTableModel()
        self.__model.setEditStrategy(QSqlTableModel.OnFieldChange)
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



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ImageNavWidget()
    w.show()
    sys.exit(app.exec())

