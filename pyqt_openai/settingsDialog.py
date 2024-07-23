import os
import sys

from pyqt_openai.constants import COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE, LANGUAGE_DICT, DB_NAME_REGEX
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget

# Get the absolute path of the current script file

script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtCore import Qt, QRegularExpression
from qtpy.QtGui import QRegularExpressionValidator
from qtpy.QtWidgets import QFrame, QDialog, QComboBox, QLineEdit, QCheckBox, QSizePolicy, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QSplitter, QLabel, QDialogButtonBox, QWidget, QMessageBox


from pyqt_openai import constants
from pyqt_openai.models import SettingsParamsContainer, ImagePromptContainer, ChatThreadContainer
from pyqt_openai.lang.translations import LangClass


class SettingsDialog(QDialog):
    def __init__(self, args: SettingsParamsContainer, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.__initVal(args)
        self.__initUi()

    def __initVal(self, args):
        self.__lang = args.lang
        self.__db = args.db
        self.__do_not_ask_again = args.do_not_ask_again
        self.__notify_finish = args.notify_finish
        self.__show_toolbar = args.show_toolbar
        self.__show_secondary_toolbar = args.show_secondary_toolbar
        self.__thread_tool_widget = args.thread_tool_widget
        self.__chat_column_to_show = args.chat_column_to_show
        self.__image_column_to_show = args.image_column_to_show

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Settings"])
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)

        # Language setting
        self.__langCmbBox = QComboBox()
        self.__langCmbBox.addItems(list(LANGUAGE_DICT.keys()))
        self.__langCmbBox.setCurrentText(self.__lang)
        self.__langCmbBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Language"]))
        lay.addWidget(self.__langCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        langWidget = QWidget()
        langWidget.setLayout(lay)

        # Database setting
        dbLayout = QHBoxLayout()
        self.__dbLineEdit = QLineEdit(self.__db)
        self.__validator = QRegularExpressionValidator()
        re = QRegularExpression(DB_NAME_REGEX)
        self.__validator.setRegularExpression(re)
        self.__dbLineEdit.setValidator(self.__validator)
        dbLayout.addWidget(QLabel(LangClass.TRANSLATIONS["Name of target database (without extension)"]))
        dbLayout.addWidget(self.__dbLineEdit)

        # Checkboxes
        self.__doNotAskAgainCheckBox = QCheckBox(f'{LangClass.TRANSLATIONS["Do not ask again when closing"]} ({LangClass.TRANSLATIONS["Always close the application"]})')
        self.__doNotAskAgainCheckBox.setChecked(self.__do_not_ask_again)

        self.__notifyFinishCheckBox = QCheckBox(LangClass.TRANSLATIONS["Notify when finish processing any task (Conversion, etc.)"])
        self.__notifyFinishCheckBox.setChecked(self.__notify_finish)
        self.__showToolbarCheckBox = QCheckBox(LangClass.TRANSLATIONS["Show Toolbar"])
        self.__showToolbarCheckBox.setChecked(self.__show_toolbar)
        self.__showSecondaryToolBarChkBox = QCheckBox(LangClass.TRANSLATIONS['Show Secondary Toolbar'])
        self.__showSecondaryToolBarChkBox.setChecked(self.__show_secondary_toolbar)
        self.__showThreadToolWidgetChkBox = QCheckBox(LangClass.TRANSLATIONS['Show Find Tool'])
        self.__showThreadToolWidgetChkBox.setChecked(self.__thread_tool_widget)

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.__accept)
        buttonBox.rejected.connect(self.reject)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        lay = QVBoxLayout()
        lay.addWidget(langWidget)
        lay.addLayout(dbLayout)
        lay.addWidget(self.__doNotAskAgainCheckBox)
        lay.addWidget(self.__notifyFinishCheckBox)
        lay.addWidget(self.__showToolbarCheckBox)
        lay.addWidget(self.__showSecondaryToolBarChkBox)
        lay.addWidget(self.__showThreadToolWidgetChkBox)

        generalGrpBox = QGroupBox(LangClass.TRANSLATIONS['General'])
        generalGrpBox.setLayout(lay)

        chatColAllCheckBox = QCheckBox(LangClass.TRANSLATIONS['Check All'])
        self.__chatColCheckBoxListWidget = CheckBoxListWidget()
        for k in ChatThreadContainer.get_keys(excludes=COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE):
            self.__chatColCheckBoxListWidget.addItem(k, checked=k in self.__chat_column_to_show)

        chatColAllCheckBox.stateChanged.connect(self.__chatColCheckBoxListWidget.toggleState)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Select the columns you want to show in the chat list.']))
        lay.addWidget(chatColAllCheckBox)
        lay.addWidget(self.__chatColCheckBoxListWidget)

        chatColWidget = QWidget()
        chatColWidget.setLayout(lay)

        imageColAllCheckBox = QCheckBox(LangClass.TRANSLATIONS['Check all'])
        self.__imageColCheckBoxListWidget = CheckBoxListWidget()
        for k in ImagePromptContainer.get_keys(excludes=COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE):
            self.__imageColCheckBoxListWidget.addItem(k, checked=k in self.__image_column_to_show)

        imageColAllCheckBox.stateChanged.connect(self.__imageColCheckBoxListWidget.toggleState)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Select the columns you want to show in the image list.']))
        lay.addWidget(imageColAllCheckBox)
        lay.addWidget(self.__imageColCheckBoxListWidget)

        imageColWidget = QWidget()
        imageColWidget.setLayout(lay)

        self.__splitter = QSplitter()
        self.__splitter.addWidget(chatColWidget)
        self.__splitter.addWidget(imageColWidget)
        self.__splitter.setHandleWidth(1)
        self.__splitter.setChildrenCollapsible(False)
        self.__splitter.setSizes([500, 500])
        self.__splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        self.__splitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        lay = QVBoxLayout()
        lay.addWidget(self.__splitter)

        columnGrpBox = QGroupBox(LangClass.TRANSLATIONS['Show/hide columns'])
        columnGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(generalGrpBox)
        lay.addWidget(columnGrpBox)
        lay.addWidget(buttonBox)

        self.setLayout(lay)

    def __accept(self):
        # If DB file name is empty
        if self.__dbLineEdit.text().strip() == '':
            QMessageBox.critical(self, LangClass.TRANSLATIONS['Error'], LangClass.TRANSLATIONS['Database name cannot be empty.'])
        else:
            self.accept()

    def getParam(self):
        return SettingsParamsContainer(
            lang=self.__langCmbBox.currentText(),
            db=self.__dbLineEdit.text(),
            do_not_ask_again=self.__doNotAskAgainCheckBox.isChecked(),
            notify_finish=self.__notifyFinishCheckBox.isChecked(),
            show_toolbar=self.__showToolbarCheckBox.isChecked(),
            show_secondary_toolbar=self.__showSecondaryToolBarChkBox.isChecked(),
            thread_tool_widget=self.__showThreadToolWidgetChkBox.isChecked(),
            chat_column_to_show=COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE+self.__chatColCheckBoxListWidget.getCheckedItemsText(),
            image_column_to_show=COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE+self.__imageColCheckBoxListWidget.getCheckedItemsText()
        )