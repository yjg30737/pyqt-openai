from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QScrollArea, QWidget, QTabWidget, QGridLayout

from pyqt_openai.right_sidebar.chatPage import ChatPage
from pyqt_openai.right_sidebar.llama_widget.llamaPage import LlamaPage
from pyqt_openai.sqlite import SqliteDatabase


class AIPlaygroundWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        # load tab widget's last current index
        if self.__settings_struct.contains('TAB_IDX'):
            self.__cur_idx = int(self.__settings_struct.value('TAB_IDX'))
        else:
            self.__cur_idx = 0
            self.__settings_struct.setValue('TAB_IDX', str(self.__cur_idx))

    def __initUi(self):
        tabWidget = QTabWidget()

        chatPage = ChatPage()
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