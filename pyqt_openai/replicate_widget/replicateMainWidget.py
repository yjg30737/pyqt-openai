from __future__ import annotations

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.replicate_widget.replicateHome import ReplicateHome
from pyqt_openai.replicate_widget.replicateRightSideBar import (
    ReplicateRightSideBarWidget,
)
from pyqt_openai.widgets.imageMainWidget import ImageMainWidget


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
        CONFIG_MANAGER.set_replicate_property("show_history", f)

    def toggleSetting(self, f):
        super().toggleSetting(f)
        CONFIG_MANAGER.set_replicate_property("show_setting", f)
