from functools import partial

from qtpy.QtCore import QSettings, Signal
from qtpy.QtWidgets import QScrollArea, QWidget, QTabWidget, QGridLayout

from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.right_sidebar.chatPage import ChatPage
from pyqt_openai.right_sidebar.llama_widget.llamaPage import LlamaPage


class AIPlaygroundWidget(QScrollArea):
    onDirectorySelected = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)

        # load tab widget's last current index
        if self.__settings_ini.contains('TAB_IDX'):
            self.__cur_idx = int(self.__settings_ini.value('TAB_IDX'))
        else:
            self.__cur_idx = 0
            self.__settings_ini.setValue('TAB_IDX', str(self.__cur_idx))

        if self.__settings_ini.contains('use_llama_index'):
            self.__use_llama_index = self.__settings_ini.value('use_llama_index', type=bool)
        else:
            self.__use_llama_index = False
            self.__settings_ini.setValue('use_llama_index', self.__use_llama_index)

        # load saved llamaindex directory
        self.__llama_index_directory = ''
        if self.__settings_ini.contains('llama_index_directory'):
            self.__llama_index_directory = self.__settings_ini.value('llama_index_directory', type=str)

    def __initUi(self):
        tabWidget = QTabWidget()

        chatPage = ChatPage()
        self.__llamaPage = LlamaPage()
        self.__llamaPage.onDirectorySelected.connect(self.__onDirectorySelected)

        tabWidget.addTab(chatPage, LangClass.TRANSLATIONS['Chat'], )
        tabWidget.addTab(self.__llamaPage, 'LlamaIndex', )
        tabWidget.currentChanged.connect(self.__tabChanged)
        tabWidget.setTabEnabled(1, self.__use_llama_index)
        tabWidget.setCurrentIndex(self.__cur_idx)

        partial_func = partial(tabWidget.setTabEnabled, 1)
        chatPage.onToggleLlama.connect(lambda x: partial_func(x))

        lay = QGridLayout()
        lay.addWidget(tabWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

        self.setStyleSheet('QScrollArea { border: 0 }')

    def __tabChanged(self, idx):
        self.__settings_ini.setValue('TAB_IDX', idx)

    def __onDirectorySelected(self, selected_dirname):
        self.__llama_index_directory = selected_dirname
        self.__settings_ini.setValue('llama_index_directory', selected_dirname)
        self.onDirectorySelected.emit(selected_dirname)