import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget, QHBoxLayout, QVBoxLayout, QWidget, QSplitter

from pyqt_openai import ICON_HISTORY, ICON_SETTING, DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW, \
    DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.globals import DB
from pyqt_openai.replicate_widget.replicateHome import ReplicateHome
from pyqt_openai.replicate_widget.replicateRightSideBar import ReplicateRightSideBarWidget
from pyqt_openai.util.script import get_image_filename_for_saving, open_directory, get_image_prompt_filename_for_saving, \
    getSeparator
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.imageMainWidget import ImageMainWidget
from pyqt_openai.widgets.imageNavWidget import ImageNavWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.thumbnailView import ThumbnailView


class ReplicateMainWidget(ImageMainWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self._homePage = ReplicateHome()
        self._rightSideBarWidget = ReplicateRightSideBarWidget()

        self._setHomeWidget(self._homePage)
        self._setRightSideBarWidget(self._rightSideBarWidget)
        self._completeUi()

    def toggleHistory(self, f):
        super().toggleHistory(f)
        CONFIG_MANAGER.set_replicate_property('show_history', f)

    def toggleSetting(self, f):
        super().toggleSetting(f)
        CONFIG_MANAGER.set_replicate_property('show_setting', f)
