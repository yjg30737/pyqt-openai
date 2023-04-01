from qtpy.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QListWidgetItem, \
    QLabel

from pyqt_openai.convListWidget import ConvListWidget
from pyqt_openai.searchBar import SearchBar
from pyqt_openai.svgButton import SvgButton


class LeftSideBar(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        searchBar = SearchBar()
        searchBar.searched.connect(self.__search)
        searchBar.setPlaceHolder('Search the Conversation...')

        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()
        self.__clearBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')
        self.__clearBtn.setIcon('ico/clear.svg')

        self.__addBtn.setToolTip('Add')
        self.__delBtn.setToolTip('Delete')
        self.__clearBtn.setToolTip('Clear')

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)
        self.__clearBtn.clicked.connect(self.__clear)

        lay = QHBoxLayout()
        lay.addWidget(searchBar)
        lay.setContentsMargins(0, 0, 2, 0)
        lay.setSpacing(0)

        topLeftWidget = QWidget()
        topLeftWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__clearBtn)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        topRightWidget = QWidget()
        topRightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(topLeftWidget)
        lay.addWidget(topRightWidget)
        topWidget = QWidget()
        topWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.__convListWidget = ConvListWidget()
        self.__convListWidget.addConv('New Chat')
        self.__convListWidget.addConv('New Chat')
        self.__convListWidget.addConv('New Chat')

        self.__convListWidget.setAlternatingRowColors(True)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__convListWidget)

        self.setLayout(lay)

    def __add(self):
        self.__convListWidget.addConv('A')

    def __delete(self):
        self.__convListWidget.deleteConv()

    def __clear(self):
        self.__convListWidget.clearConv()

    def __search(self, text):
        for i in range(self.__convListWidget.count()):
            item = self.__convListWidget.item(i)
            widget = self.__convListWidget.itemWidget(item)
            item.setHidden(False if text.lower() in widget.text().lower() else True)
