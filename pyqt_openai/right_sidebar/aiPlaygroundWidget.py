from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QScrollArea, QWidget, QTabWidget, QGridLayout

from pyqt_openai.right_sidebar.chatPage import ChatPage
from pyqt_openai.right_sidebar.llama_widget.llamaPage import LlamaPage
from pyqt_openai.sqlite import SqliteDatabase


class AIPlaygroundWidget(QScrollArea):
    def __init__(self, db: SqliteDatabase, ini_etc_dict, model_data):
        super().__init__()
        self.__initVal(db, ini_etc_dict, model_data)
        self.__initUi()

    def __initVal(self, db, ini_etc_dict, model_data):
        self.__db = db
        self.__modelData = model_data

        self.__ini_etc_dict = ini_etc_dict
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        # load tab widget's last current index
        if self.__settings_struct.contains('TAB_IDX'):
            self.__cur_idx = int(self.__settings_struct.value('TAB_IDX'))
        else:
            self.__cur_idx = 0
            self.__settings_struct.setValue('TAB_IDX', str(self.__cur_idx))

    def __initUi(self):
        tabWidget = QTabWidget()

        chatPage = ChatPage(self.__db, self.__ini_etc_dict)
        self.__llamaPage = LlamaPage()

        tabWidget.addTab(chatPage, 'Chat', )
        tabWidget.addTab(self.__llamaPage, 'LlamaIndex', )
        tabWidget.currentChanged.connect(self.__tabChanged)
        tabWidget.setCurrentIndex(self.__cur_idx)

        lay = QGridLayout()
        lay.addWidget(tabWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

        self.setStyleSheet('QScrollArea { border: 0 }')

    def __tabChanged(self, idx):
        self.__settings_struct.setValue('TAB_IDX', idx)