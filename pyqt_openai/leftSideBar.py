from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from pyqt_openai.svgButton import SvgButton


class LeftSideBar(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
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
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(self.__clearBtn)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        btnWidget = QWidget()
        btnWidget.setLayout(lay)

        convListWidget = QListWidget()
        convListWidget.addItems(['A', 'B', 'C'])

        lay = QVBoxLayout()
        lay.addWidget(btnWidget)
        lay.addWidget(convListWidget)

        self.setLayout(lay)

    def __add(self):
        print('add')

    def __delete(self):
        print('delete')

    def __clear(self):
        print('clear')