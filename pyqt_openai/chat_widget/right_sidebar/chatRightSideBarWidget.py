from __future__ import annotations

from functools import partial

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QGridLayout, QMessageBox, QScrollArea, QTabWidget, QWidget

from pyqt_openai.chat_widget.right_sidebar.llama_widget.llamaPage import LlamaPage
from pyqt_openai.chat_widget.right_sidebar.usingAPIPage import UsingAPIPage
from pyqt_openai.chat_widget.right_sidebar.usingG4FPage import UsingG4FPage
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.globals import LLAMAINDEX_WRAPPER
from pyqt_openai.lang.translations import LangClass


class ChatRightSideBarWidget(QScrollArea):
    onTabChanged = Signal(int)
    onToggleJSON = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__cur_idx = CONFIG_MANAGER.get_general_property("TAB_IDX")
        self.__use_llama_index = CONFIG_MANAGER.get_general_property("use_llama_index")
        self.__llama_index_directory = CONFIG_MANAGER.get_general_property(
            "llama_index_directory",
        )

    def __initUi(self):
        tabWidget = QTabWidget()
        tabWidget.currentChanged.connect(self.onTabChanged.emit)

        usingG4FPage = UsingG4FPage()
        usingAPIPage = UsingAPIPage()
        self.__llamaPage = LlamaPage()
        self.__llamaPage.onDirectorySelected.connect(self.__onDirectorySelected)

        # TODO LANGUAGE
        tabWidget.addTab(usingG4FPage, "Using G4F (Free)")
        tabWidget.addTab(usingAPIPage, "Using API")
        tabWidget.addTab(self.__llamaPage, "LlamaIndex")
        tabWidget.currentChanged.connect(self.__tabChanged)
        tabWidget.setTabEnabled(2, self.__use_llama_index)
        tabWidget.setCurrentIndex(self.__cur_idx)

        partial_func = partial(tabWidget.setTabEnabled, 2)
        usingAPIPage.onToggleLlama.connect(lambda x: partial_func(x))
        usingAPIPage.onToggleJSON.connect(self.onToggleJSON)

        lay = QGridLayout()
        lay.addWidget(tabWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

        self.setStyleSheet("QScrollArea { border: 0 }")

    def __tabChanged(self, idx):
        self.__cur_idx = idx
        CONFIG_MANAGER.set_general_property("TAB_IDX", self.__cur_idx)

    def __onDirectorySelected(self, selected_dirname):
        self.__llama_index_directory = selected_dirname
        CONFIG_MANAGER.set_general_property("llama_index_directory", selected_dirname)
        try:
            LLAMAINDEX_WRAPPER.set_directory(selected_dirname)
        except Exception as e:
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], str(e))


    def currentTabIdx(self):
        return self.__cur_idx
