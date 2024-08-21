from functools import partial

from qtpy.QtCore import QSettings, Signal
from qtpy.QtWidgets import QScrollArea, QWidget, QTabWidget, QGridLayout

from pyqt_openai import INI_FILE_NAME
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.gpt_widget.right_sidebar.chatPage import ChatPage
from pyqt_openai.gpt_widget.right_sidebar.llama_widget.llamaPage import LlamaPage


class GPTRightSideBarWidget(QScrollArea):
    onDirectorySelected = Signal(str)
    onToggleJSON = Signal(bool)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__cur_idx = CONFIG_MANAGER.get_general_property('TAB_IDX')
        self.__use_llama_index = CONFIG_MANAGER.get_general_property('use_llama_index')
        self.__llama_index_directory = CONFIG_MANAGER.get_general_property('llama_index_directory')

    def __initUi(self):
        tabWidget = QTabWidget()

        chatPage = ChatPage()
        self.__llamaPage = LlamaPage()
        self.__llamaPage.onDirectorySelected.connect(self.__onDirectorySelected)

        tabWidget.addTab(chatPage, LangClass.TRANSLATIONS['GPT'], )
        tabWidget.addTab(self.__llamaPage, 'LlamaIndex', )
        tabWidget.currentChanged.connect(self.__tabChanged)
        tabWidget.setTabEnabled(1, self.__use_llama_index)
        tabWidget.setCurrentIndex(self.__cur_idx)

        partial_func = partial(tabWidget.setTabEnabled, 1)
        chatPage.onToggleLlama.connect(lambda x: partial_func(x))
        chatPage.onToggleJSON.connect(self.onToggleJSON)

        lay = QGridLayout()
        lay.addWidget(tabWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

        self.setStyleSheet('QScrollArea { border: 0 }')

    def __tabChanged(self, idx):
        CONFIG_MANAGER.set_general_property('TAB_IDX', idx)

    def __onDirectorySelected(self, selected_dirname):
        self.__llama_index_directory = selected_dirname
        CONFIG_MANAGER.set_general_property('llama_index_directory', selected_dirname)
        self.onDirectorySelected.emit(selected_dirname)