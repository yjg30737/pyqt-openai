from __future__ import annotations

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.g4f_image_widget.g4fImageHome import G4FImageHome
from pyqt_openai.g4f_image_widget.g4fImageRightSideBar import G4FImageRightSideBarWidget
from pyqt_openai.widgets.imageMainWidget import ImageMainWidget


class G4FImageMainWidget(ImageMainWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self._homePage = G4FImageHome()
        self._rightSideBarWidget = G4FImageRightSideBarWidget()

        self._setHomeWidget(self._homePage)
        self._setRightSideBarWidget(self._rightSideBarWidget)
        self._completeUi()

    def toggleHistory(self, f):
        super().toggleHistory(f)
        CONFIG_MANAGER.set_g4f_image_property("show_history", f)

    def toggleSetting(self, f):
        super().toggleSetting(f)
        CONFIG_MANAGER.set_g4f_image_property("show_setting", f)
