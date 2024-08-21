from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, \
    QDialogButtonBox, QMessageBox

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import SettingsParamsContainer
from pyqt_openai.settings_dialog.generalSettingsWidget import GeneralSettingsWidget


class SettingsDialog(QDialog):
    def __init__(self, args: SettingsParamsContainer, parent=None):
        super().__init__(parent)
        self.__initVal(args)
        self.__initUi()

    def __initVal(self, args):
        self.__args = args

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Settings"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__generalSettingsWidget = GeneralSettingsWidget(self.__args)

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.__accept)
        buttonBox.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(self.__generalSettingsWidget)
        lay.addWidget(buttonBox)

        self.setLayout(lay)

    def __accept(self):
        # If DB file name is empty
        if self.__generalSettingsWidget.db.strip() == '':
            QMessageBox.critical(self, LangClass.TRANSLATIONS['Error'], LangClass.TRANSLATIONS['Database name cannot be empty.'])
        else:
            self.accept()

    def getParam(self):
        return SettingsParamsContainer(
            **self.__generalSettingsWidget.getParam(),
        )