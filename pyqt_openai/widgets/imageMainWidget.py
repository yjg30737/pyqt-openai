import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QSplitter,
)

from pyqt_openai import (
    ICON_HISTORY,
    ICON_SETTING,
    DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW,
    DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW,
)
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.globals import DB
from pyqt_openai.util.script import (
    get_image_filename_for_saving,
    open_directory,
    get_image_prompt_filename_for_saving,
    getSeparator,
)
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.imageNavWidget import ImageNavWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.thumbnailView import ThumbnailView


class ImageMainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # ini
        self._show_history = CONFIG_MANAGER.get_dalle_property("show_history")
        self._show_setting = CONFIG_MANAGER.get_dalle_property("show_setting")

    def __initUi(self):
        self._imageNavWidget = ImageNavWidget(
            ImagePromptContainer.get_keys(), "image_tb"
        )

        # Main widget
        # This contains home page (at the beginning of the stack) and
        # widget for main view
        self._centralWidget = QStackedWidget()

        self._viewWidget = ThumbnailView()

        self._imageNavWidget.getContent.connect(
            lambda x: self._updateCenterWidget(1, x)
        )

        self._historyBtn = Button()
        self._historyBtn.setStyleAndIcon(ICON_HISTORY)
        self._historyBtn.setCheckable(True)
        self._historyBtn.setToolTip(
            LangClass.TRANSLATIONS["History"]
            + f" ({DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW})"
        )
        self._historyBtn.setChecked(self._show_history)
        self._historyBtn.toggled.connect(self.toggleHistory)
        self._historyBtn.setShortcut(DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW)

        self._settingBtn = Button()
        self._settingBtn.setStyleAndIcon(ICON_SETTING)
        self._settingBtn.setCheckable(True)
        self._settingBtn.setToolTip(
            LangClass.TRANSLATIONS["Settings"]
            + f" ({DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW})"
        )
        self._settingBtn.setChecked(self._show_setting)
        self._settingBtn.toggled.connect(self.toggleSetting)
        self._settingBtn.setShortcut(DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW)

        lay = QHBoxLayout()
        lay.addWidget(self._historyBtn)
        lay.addWidget(self._settingBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._menuWidget = QWidget()
        self._menuWidget.setLayout(lay)
        self._menuWidget.setMaximumHeight(self._menuWidget.sizeHint().height())

        self._rightSideBarWidget = QWidget()

        self._mainWidget = QSplitter()
        self._mainWidget.addWidget(self._imageNavWidget)
        self._mainWidget.addWidget(self._centralWidget)

    def _setHomeWidget(self, home_page):
        self._homePage = home_page
        self._centralWidget.addWidget(self._homePage)
        self._centralWidget.addWidget(self._viewWidget)

    def _setRightSideBarWidget(self, right_side_bar_widget):
        self._rightSideBarWidget = right_side_bar_widget
        self._rightSideBarWidget.submit.connect(self._setResult)
        self._rightSideBarWidget.submitAllComplete.connect(
            self._imageGenerationAllComplete
        )

    def _completeUi(self):
        self._mainWidget.addWidget(self._rightSideBarWidget)
        self._mainWidget.setSizes([200, 500, 300])
        self._mainWidget.setChildrenCollapsible(False)
        self._mainWidget.setHandleWidth(2)
        self._mainWidget.setStyleSheet(
            """
        QSplitter::handle:horizontal
        {
            background: #CCC;
            height: 1px;
        }
        """
        )

        sep = getSeparator("horizontal")

        lay = QVBoxLayout()
        lay.addWidget(self._menuWidget)
        lay.addWidget(sep)
        lay.addWidget(self._mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setLayout(lay)

        # Put this below to prevent the widgets pop up when app is opened
        self._imageNavWidget.setVisible(self._show_history)
        self._rightSideBarWidget.setVisible(self._show_setting)

    def _updateCenterWidget(self, idx, data=None):
        """
        0 is home page, 1 is the main view
        :param idx: index
        :param data: data (bytes)
        """

        # Set the current index
        self._centralWidget.setCurrentIndex(idx)

        # If the index is 1, set the content
        if idx == 1 and data is not None:
            self._viewWidget.setContent(data)

    def showSecondaryToolBar(self, f):
        self._menuWidget.setVisible(f)
        CONFIG_MANAGER.set_general_property("show_secondary_toolbar", f)

    def toggleButtons(self, x):
        self._historyBtn.setChecked(x)
        self._settingBtn.setChecked(x)

    def setAIEnabled(self, f):
        self._rightSideBarWidget.setEnabled(f)

    def _setResult(self, result):
        self._updateCenterWidget(1, result.data)
        # save
        if self._rightSideBarWidget.isSavedEnabled():
            self._saveResultImage(result)
        DB.insertImage(result)
        self._imageNavWidget.refresh()

    def _saveResultImage(self, result):
        directory = self._rightSideBarWidget.getDirectory()
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, get_image_filename_for_saving(result))
        with open(filename, "wb") as f:
            f.write(result.data)

        if self._rightSideBarWidget.getSavePromptAsText():
            txt_filename = get_image_prompt_filename_for_saving(directory, filename)
            with open(txt_filename, "w") as f:
                f.write(result.prompt)

    def _imageGenerationAllComplete(self):
        if not self.isVisible() or not self.window().isActiveWindow():
            if CONFIG_MANAGER.get_general_property("notify_finish"):
                self.__notifierWidget = NotifierWidget(
                    informative_text=LangClass.TRANSLATIONS["Response 👌"],
                    detailed_text=LangClass.TRANSLATIONS["Image Generation complete."],
                )
                self.__notifierWidget.show()
                self.__notifierWidget.doubleClicked.connect(self._bringWindowToFront)

                open_directory(self._rightSideBarWidget.getDirectory())

    def _bringWindowToFront(self):
        window = self.window()
        window.showNormal()
        window.raise_()
        window.activateWindow()

    def showEvent(self, event):
        self._imageNavWidget.refresh()
        super().showEvent(event)

    def setColumns(self, columns):
        self._imageNavWidget.setColumns(columns)

    def toggleHistory(self, f):
        self._imageNavWidget.setVisible(f)
        self._show_history = f

    def toggleSetting(self, f):
        self._rightSideBarWidget.setVisible(f)
        self._show_setting = f
