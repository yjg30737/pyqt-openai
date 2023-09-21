from pyqt_openai.convListWidget import ConvListWidget
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.searchBar import SearchBar
from pyqt_openai.svgButton import SvgButton
from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QWidget, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QListWidgetItem


class LeftSideBar(QWidget):
    added = Signal()
    changed = Signal(QListWidgetItem)
    deleted = Signal(list)
    convUpdated = Signal(int, str)
    export = Signal(list)

    def __init__(self, db):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db

    def __initUi(self):
        searchBar = SearchBar()
        searchBar.searched.connect(self.__search)
        searchBar.setPlaceHolder('Search the Conversation...')

        self.__searchOptionCmbBox = QComboBox()
        self.__searchOptionCmbBox.addItems([LangClass.TRANSLATIONS['Title'], LangClass.TRANSLATIONS['Content']])
        self.__searchOptionCmbBox.setMinimumHeight(searchBar.sizeHint().height())

        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()
        self.__saveBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')
        self.__saveBtn.setIcon('ico/save.svg')

        self.__addBtn.setToolTip(LangClass.TRANSLATIONS['Add'])
        self.__delBtn.setToolTip(LangClass.TRANSLATIONS['Delete'])
        self.__saveBtn.setToolTip(LangClass.TRANSLATIONS['Save'])

        self.__addBtn.clicked.connect(self.__addClicked)
        self.__delBtn.clicked.connect(self.__deleteClicked)
        self.__saveBtn.clicked.connect(self.__saveClicked)

        self.__allCheckBox = QCheckBox(LangClass.TRANSLATIONS['Check All'])
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

        lay = QHBoxLayout()
        lay.addWidget(searchBar)
        lay.addWidget(self.__searchOptionCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        searchWidget = QWidget()
        searchWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(navWidget)
        lay.addWidget(searchWidget)

        topWidget = QWidget()
        topWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__convListWidget = ConvListWidget()
        self.__convListWidget.changed.connect(self.changed)
        self.__convListWidget.convUpdated.connect(self.convUpdated)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__convListWidget)

        self.setLayout(lay)

    def __addClicked(self):
        self.added.emit()

    def addToList(self, id):
        self.__convListWidget.addConv(LangClass.TRANSLATIONS['New Chat'], id)
        self.__convListWidget.setCurrentRow(0)

    def isCurrentConvExists(self):
        return self.__convListWidget.count() > 0 and self.__convListWidget.currentItem()

    def __deleteClicked(self):
        # get the ID of row, not actual index (because list is in a stacked form)
        rows = self.__convListWidget.getCheckedRowsIds()
        self.__convListWidget.removeCheckedRows()
        self.deleted.emit(rows)
        self.__allCheckBox.setChecked(False)

    def __saveClicked(self):
        self.export.emit(self.__convListWidget.getCheckedRowsIds())

    def __stateChanged(self, f):
        self.__convListWidget.toggleState(f)

    def __search(self, text):
        # title
        if self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS['Title']:
            for i in range(self.__convListWidget.count()):
                item = self.__convListWidget.item(i)
                if item:
                    widget = self.__convListWidget.itemWidget(item)
                    item.setHidden(False if text.lower() in widget.text().lower() else True)
        # content
        elif self.__searchOptionCmbBox.currentText() == LangClass.TRANSLATIONS['Content']:
            convs = self.__db.selectAllContentOfConv()
            db_id_real_id_dict = dict()
            for i in range(self.__convListWidget.count()):
                db_id_real_id_dict[self.__convListWidget.item(i).data(Qt.UserRole)] = self.__convListWidget.item(i)
            for conv in convs:
                i = conv[0]
                each_content_arr = list(filter(lambda x: x.find(text) != -1, [_['conv'] for _ in conv[1]]))
                item = db_id_real_id_dict[i]
                if item:
                    if len(each_content_arr) > 0:
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
                    print('id:', conv[0])
                    print('conv:', [(_['id'], _['conv']) for _ in conv[1]])

    def initHistory(self, db):
        try:
            conv_lst = db.selectAllConv()
            for conv in conv_lst:
                id, title = conv[0], conv[1]
                self.__convListWidget.addConv(title, id)
        except Exception as e:
            print(e)