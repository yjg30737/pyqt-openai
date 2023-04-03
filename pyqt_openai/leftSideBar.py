from qtpy.QtCore import Signal
from qtpy.QtWidgets import QWidget, QCheckBox, QListWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QListWidgetItem, \
    QLabel

from pyqt_openai.convListWidget import ConvListWidget
from pyqt_openai.searchBar import SearchBar
from pyqt_openai.svgButton import SvgButton


class LeftSideBar(QWidget):
    added = Signal()
    changed = Signal(int)
    deleted = Signal(list)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        searchBar = SearchBar()
        searchBar.searched.connect(self.__search)
        searchBar.setPlaceHolder('Search the Conversation...')

        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()
        self.__saveBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')
        self.__saveBtn.setIcon('ico/download.svg')

        self.__addBtn.setToolTip('Add')
        self.__delBtn.setToolTip('Delete')
        self.__saveBtn.setToolTip('Save (testing)')

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)
        self.__saveBtn.clicked.connect(self.__save)

        self.__allCheckBox = QCheckBox('Check All')
        self.__allCheckBox.stateChanged.connect(self.__stateChanged)

        lay = QHBoxLayout()
        lay.addWidget(self.__allCheckBox)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__saveBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        navWidget = QWidget()
        navWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(navWidget)
        lay.addWidget(searchBar)

        topWidget = QWidget()
        topWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__convListWidget = ConvListWidget()
        self.__convListWidget.addConv('New Chat')
        self.__convListWidget.currentRowChanged.connect(self.changed)

        self.__convListWidget.setAlternatingRowColors(True)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__convListWidget)

        self.setLayout(lay)

    def __add(self):
        self.__convListWidget.addConv('New Chat')
        self.__convListWidget.setCurrentRow(0)
        self.added.emit()

    def __delete(self):
        rows = self.__convListWidget.getCheckedRows()
        self.__convListWidget.removeCheckedRows()
        self.deleted.emit(rows)

    def __save(self):
        print('save')

    def __stateChanged(self, f):
        self.__convListWidget.toggleState(f)

    def __search(self, text):
        for i in range(self.__convListWidget.count()):
            item = self.__convListWidget.item(i)
            widget = self.__convListWidget.itemWidget(item)
            item.setHidden(False if text.lower() in widget.text().lower() else True)
