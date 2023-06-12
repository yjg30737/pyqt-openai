import json

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QWidget, QCheckBox, QListWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QListWidgetItem, \
    QLabel

from pyqt_openai.image_gen_widget.imageListWidget import ImageListWidget
from pyqt_openai.searchBar import SearchBar
from pyqt_openai.svgButton import SvgButton


class LeftSideBar(QWidget):
    added = Signal()
    changed = Signal(QListWidgetItem)
    deleted = Signal(list)
    imageUpdated = Signal(int, str)
    export = Signal(list)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        searchBar = SearchBar()
        searchBar.searched.connect(self.__search)
        searchBar.setPlaceHolder('Search the image group...')

        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()
        self.__saveBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')
        self.__saveBtn.setIcon('ico/save.svg')

        self.__addBtn.setToolTip('Add')
        self.__delBtn.setToolTip('Delete')
        self.__saveBtn.setToolTip('Save')

        self.__addBtn.clicked.connect(self.__addClicked)
        self.__delBtn.clicked.connect(self.__deleteClicked)
        self.__saveBtn.clicked.connect(self.__saveClicked)

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

        self.__imageListWidget = ImageListWidget()
        # self.__imageListWidget.changed.connect(self.changed)
        # self.__imageListWidget.imageUpdated.connect(self.imageUpdated)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__imageListWidget)

        self.setLayout(lay)

    def __addClicked(self):
        self.added.emit()

    def addImageGroup(self, id):
        self.__imageListWidget.addImage('New Chat', id)
        self.__imageListWidget.setCurrentRow(0)
    # 
    # def isCurrentImageExists(self):
    #     return self.__imageListWidget.count() > 0 and self.__imageListWidget.currentItem()
    # 
    def __deleteClicked(self):
        # get the ID of row, not actual index (because list is in a stacked form)
        rows = self.__imageListWidget.getCheckedRowsIds()
        self.__imageListWidget.removeCheckedRows()
        self.deleted.emit(rows)
        self.__allCheckBox.setChecked(False)

    def __saveClicked(self):
        self.export.emit(self.__imageListWidget.getCheckedRowsIds())
    # 
    def __stateChanged(self, f):
        self.__imageListWidget.toggleState(f)
    # 
    def __search(self, text):
        for i in range(self.__imageListWidget.count()):
            item = self.__imageListWidget.item(i)
            widget = self.__imageListWidget.itemWidget(item)
            item.setHidden(False if text.lower() in widget.text().lower() else True)
    # 
    # def initHistory(self, db):
    #     try:
    #         image_lst = db.selectAllImage()
    #         for image in image_lst:
    #             id, title = image[0], image[1]
    #             self.__imageListWidget.addImage(title, id)
    #     except Exception as e:
    #         print(e)