import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget, QHBoxLayout, QVBoxLayout, QWidget, QSplitter

from pyqt_openai import ICON_HISTORY, ICON_SETTING, DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW, \
    DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.replicate_widget.replicateHome import ReplicateHome
from pyqt_openai.replicate_widget.replicateRightSideBar import ReplicateRightSideBarWidget
from pyqt_openai.util.script import get_image_filename_for_saving, open_directory, get_image_prompt_filename_for_saving, \
    getSeparator
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.imageNavWidget import ImageNavWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.thumbnailView import ThumbnailView


class ReplicateMainWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__show_history = CONFIG_MANAGER.get_replicate_property('show_history')
        self.__show_setting = CONFIG_MANAGER.get_replicate_property('show_setting')

    def __initUi(self):
        self.__imageNavWidget = ImageNavWidget(ImagePromptContainer.get_keys(), 'image_tb')

        # Main widget
        # This contains home page (at the beginning of the stack) and
        # widget for main view
        self.__mainWidget = QStackedWidget()

        self.__homePage = ReplicateHome()
        self.__viewWidget = ThumbnailView()

        self.__mainWidget.addWidget(self.__homePage)
        self.__mainWidget.addWidget(self.__viewWidget)

        self.__rightSideBarWidget = ReplicateRightSideBarWidget()

        self.__imageNavWidget.getContent.connect(lambda x: self.__updateCenterWidget(1, x))

        self.__rightSideBarWidget.submitReplicate.connect(self.__setResult)
        self.__rightSideBarWidget.submitReplicateAllComplete.connect(self.__imageGenerationAllComplete)

        self.__historyBtn = Button()
        self.__historyBtn.setStyleAndIcon(ICON_HISTORY)
        self.__historyBtn.setCheckable(True)
        self.__historyBtn.setToolTip(LangClass.TRANSLATIONS['History'] + f' ({DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW})')
        self.__historyBtn.setChecked(self.__show_history)
        self.__historyBtn.toggled.connect(self.toggleHistory)
        self.__historyBtn.setShortcut(DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW)

        self.__settingBtn = Button()
        self.__settingBtn.setStyleAndIcon(ICON_SETTING)
        self.__settingBtn.setCheckable(True)
        self.__settingBtn.setToolTip(LangClass.TRANSLATIONS['Settings'] + f' ({DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW})')
        self.__settingBtn.setChecked(self.__show_setting)
        self.__settingBtn.toggled.connect(self.toggleSetting)
        self.__settingBtn.setShortcut(DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW)

        lay = QHBoxLayout()
        lay.addWidget(self.__historyBtn)
        lay.addWidget(self.__settingBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = getSeparator('horizontal')

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__imageNavWidget)
        mainWidget.addWidget(self.__mainWidget)
        mainWidget.addWidget(self.__rightSideBarWidget)
        mainWidget.setSizes([200, 500, 300])
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setHandleWidth(2)
        mainWidget.setStyleSheet(
        '''
        QSplitter::handle:horizontal
        {
            background: #CCC;
            height: 1px;
        }
        ''')

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
        lay.addWidget(sep)
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setLayout(lay)

        # Put this below to prevent the widgets pop up when app is opened
        self.__imageNavWidget.setVisible(self.__show_history)
        self.__rightSideBarWidget.setVisible(self.__show_setting)

    def showSecondaryToolBar(self, f):
        self.__menuWidget.setVisible(f)
        CONFIG_MANAGER.set_general_property('show_secondary_toolbar', f)

    def toggleButtons(self, x):
        self.__historyBtn.setChecked(x)
        self.__settingBtn.setChecked(x)

    def __updateCenterWidget(self, idx, data=None):
        """
        0 is home page, 1 is the main view
        :param idx: index
        :param data: data (bytes)
        """

        # Set the current index
        self.__mainWidget.setCurrentIndex(idx)

        # If the index is 1, set the content
        if idx == 1 and data is not None:
            self.__viewWidget.setContent(data)

    def setAIEnabled(self, f):
        self.__rightSideBarWidget.setEnabled(f)

    def __setResult(self, result):
        self.__updateCenterWidget(1, result.data)
        # save
        if self.__rightSideBarWidget.isSavedEnabled():
            self.__saveResultImage(result)
        DB.insertImage(result)
        self.__imageNavWidget.refresh()

    def __saveResultImage(self, result):
        directory = self.__rightSideBarWidget.getDirectory()
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, get_image_filename_for_saving(result))
        with open(filename, 'wb') as f:
            f.write(result.data)

        if self.__rightSideBarWidget.getSavePromptAsText():
            txt_filename = get_image_prompt_filename_for_saving(directory, filename)
            with open(txt_filename, 'w') as f:
                f.write(result.prompt)

    def __imageGenerationAllComplete(self):
        if not self.isVisible() or not self.window().isActiveWindow():
            if CONFIG_MANAGER.get_general_property('notify_finish'):
                self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = LangClass.TRANSLATIONS['Image Generation complete.'])
                self.__notifierWidget.show()
                self.__notifierWidget.doubleClicked.connect(self.__bringWindowToFront)

                open_directory(self.__rightSideBarWidget.getDirectory())

    def __bringWindowToFront(self):
        window = self.window()
        window.showNormal()
        window.raise_()
        window.activateWindow()

    def showEvent(self, event):
        self.__imageNavWidget.refresh()
        super().showEvent(event)

    def setColumns(self, columns):
        self.__imageNavWidget.setColumns(columns)

    def toggleHistory(self, f):
        self.__imageNavWidget.setVisible(f)
        self.__show_history = f
        CONFIG_MANAGER.set_replicate_property('show_history', f)

    def toggleSetting(self, f):
        self.__rightSideBarWidget.setVisible(f)
        self.__show_setting = f
        CONFIG_MANAGER.set_replicate_property('show_setting', f)
