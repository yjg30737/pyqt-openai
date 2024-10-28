from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QMessageBox,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
)

from pyqt_openai.chat_widget.right_sidebar.apiWidget import ApiWidget
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import SettingsParamsContainer
from pyqt_openai.settings_dialog.generalSettingsWidget import GeneralSettingsWidget
from pyqt_openai.settings_dialog.voiceSettingsWidget import VoiceSettingsWidget
from pyqt_openai.widgets.navWidget import NavBar


class SettingsDialog(QDialog):
    def __init__(self, default_index=0, parent=None):
        super().__init__(parent)
        self.__initVal(default_index)
        self.__initUi()

    def __initVal(self, default_index):
        self.__default_index = default_index

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Settings"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__generalSettingsWidget = GeneralSettingsWidget()
        self.__apiWidget = ApiWidget()
        self.__voiceSettingsWidget = VoiceSettingsWidget()

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.__accept)
        buttonBox.rejected.connect(self.reject)

        self.__stackedWidget = QStackedWidget()

        self.__navBar = NavBar(orientation=Qt.Orientation.Vertical)
        self.__navBar.add(LangClass.TRANSLATIONS["General"])
        self.__navBar.add(LangClass.TRANSLATIONS["API Key"])
        self.__navBar.add(LangClass.TRANSLATIONS["TTS-STT Settings"])
        self.__navBar.itemClicked.connect(self.__currentWidgetChanged)

        self.__stackedWidget.addWidget(self.__generalSettingsWidget)
        self.__stackedWidget.addWidget(self.__apiWidget)
        self.__stackedWidget.addWidget(self.__voiceSettingsWidget)

        self.__stackedWidget.setCurrentIndex(self.__default_index)
        self.__navBar.setActiveButton(self.__default_index)

        lay = QHBoxLayout()
        lay.addWidget(self.__navBar)
        lay.addWidget(self.__stackedWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__mainWidget = QWidget()
        self.__mainWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__mainWidget)
        lay.addWidget(buttonBox)

        self.setLayout(lay)

    def __accept(self):
        # If DB file name is empty
        if self.__generalSettingsWidget.db.strip() == "":
            QMessageBox.critical(
                self,
                LangClass.TRANSLATIONS["Error"],
                LangClass.TRANSLATIONS["Database name cannot be empty."],
            )
        else:
            self.accept()

    def getParam(self):
        return SettingsParamsContainer(
            **self.__generalSettingsWidget.getParam(),
            **self.__voiceSettingsWidget.getParam(),
        )

    def __currentWidgetChanged(self, i):
        self.__stackedWidget.setCurrentIndex(i)
        self.__navBar.setActiveButton(i)
