from qtpy.QtCore import Qt
from qtpy.QtWidgets import QStackedWidget, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QDialog, QVBoxLayout, \
    QDialogButtonBox, QMessageBox

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import SettingsParamsContainer
from pyqt_openai.settings_dialog.generalSettingsWidget import GeneralSettingsWidget
from pyqt_openai.settings_dialog.markdownSettingsWidget import MarkdownSettingsWidget
from pyqt_openai.settings_dialog.shortcutSettingsWidget import ShortcutSettingsWidget


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
        self.__markdownSettingsWidget = MarkdownSettingsWidget(self.__args)
        self.__shortcutSettingsWidget = ShortcutSettingsWidget(self.__args)

        listWidget = QListWidget()
        listWidget.addItem(QListWidgetItem(LangClass.TRANSLATIONS["General Settings"]))
        listWidget.addItem(QListWidgetItem(LangClass.TRANSLATIONS["Markdown Settings"]))
        listWidget.addItem(QListWidgetItem(LangClass.TRANSLATIONS["Shortcut Settings"]))

        rightWidget = QStackedWidget()
        rightWidget.addWidget(self.__generalSettingsWidget)
        rightWidget.addWidget(self.__markdownSettingsWidget)
        rightWidget.addWidget(self.__shortcutSettingsWidget)

        lay = QHBoxLayout()
        lay.addWidget(listWidget)
        lay.addWidget(rightWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.__accept)
        buttonBox.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.addWidget(buttonBox)

        self.setLayout(lay)

        listWidget.clicked.connect(lambda: rightWidget.setCurrentIndex(listWidget.currentRow()))

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