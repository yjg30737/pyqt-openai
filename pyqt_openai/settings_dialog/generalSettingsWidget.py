from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QSplitter,
    QLabel,
    QWidget,
    QSpinBox,
    QScrollArea,
)

from pyqt_openai import (
    COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_CHAT,
    COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_IMAGE,
    LANGUAGE_DICT,
    DB_NAME_REGEX,
    MAXIMUM_MESSAGES_IN_PARAMETER_RANGE, DEFAULT_WARNING_COLOR,
)
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer, ChatThreadContainer
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget


class GeneralSettingsWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.lang = CONFIG_MANAGER.get_general_property("lang")
        self.db = CONFIG_MANAGER.get_general_property("db")
        self.do_not_ask_again = CONFIG_MANAGER.get_general_property("do_not_ask_again")
        self.notify_finish = CONFIG_MANAGER.get_general_property("notify_finish")
        self.show_secondary_toolbar = CONFIG_MANAGER.get_general_property(
            "show_secondary_toolbar"
        )
        self.chat_column_to_show = CONFIG_MANAGER.get_general_property(
            "chat_column_to_show"
        )
        self.image_column_to_show = CONFIG_MANAGER.get_general_property(
            "image_column_to_show"
        )
        self.maximum_messages_in_parameter = CONFIG_MANAGER.get_general_property(
            "maximum_messages_in_parameter"
        )
        self.show_as_markdown = CONFIG_MANAGER.get_general_property("show_as_markdown")
        self.run_at_startup = CONFIG_MANAGER.get_general_property("run_at_startup")
        self.manual_update = CONFIG_MANAGER.get_general_property("manual_update")

    def __initUi(self):
        # Language setting
        self.__langCmbBox = QComboBox()
        self.__langCmbBox.addItems(list(LANGUAGE_DICT.keys()))
        self.__langCmbBox.setCurrentText(self.lang)
        self.__langCmbBox.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Language"]))
        lay.addWidget(self.__langCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        langWidget = QWidget()
        langWidget.setLayout(lay)

        # Database setting
        dbLayout = QHBoxLayout()
        self.__dbLineEdit = QLineEdit(self.db)
        self.__validator = QRegularExpressionValidator()
        re = QRegularExpression(DB_NAME_REGEX)
        self.__validator.setRegularExpression(re)
        self.__dbLineEdit.setValidator(self.__validator)
        dbLayout.addWidget(
            QLabel(
                LangClass.TRANSLATIONS["Name of target database (without extension)"]
            )
        )
        dbLayout.addWidget(self.__dbLineEdit)

        # Checkboxes
        self.__doNotAskAgainCheckBox = QCheckBox(
            f'{LangClass.TRANSLATIONS["Do not ask again when closing"]} ({LangClass.TRANSLATIONS["Always close the application"]})'
        )
        self.__doNotAskAgainCheckBox.setChecked(self.do_not_ask_again)

        self.__notifyFinishCheckBox = QCheckBox(
            LangClass.TRANSLATIONS[
                "Notify when finish processing any task (Conversion, etc.)"
            ]
        )
        self.__notifyFinishCheckBox.setChecked(self.notify_finish)
        self.__showSecondaryToolBarChkBox = QCheckBox(
            LangClass.TRANSLATIONS["Show Secondary Toolbar"]
        )
        self.__showSecondaryToolBarChkBox.setChecked(self.show_secondary_toolbar)
        # TODO LANGUAGE
        self.__runAtStartupCheckBox = QCheckBox(
            LangClass.TRANSLATIONS["Run at startup (Windows only)"]
        )
        self.__runAtStartupCheckBox.setChecked(self.run_at_startup)

        self.__manual_updateCheckBox = QCheckBox(
            LangClass.TRANSLATIONS["Manual Update (<-> Auto Update)"]
        )
        self.__manual_updateCheckBox.setChecked(self.manual_update)

        self.__manual_UpdateWarning = QLabel(
            LangClass.TRANSLATIONS["Auto-update is supported on Windows only."]
        )
        self.__manual_UpdateWarning.setStyleSheet(f"color: {DEFAULT_WARNING_COLOR};")

        lay = QVBoxLayout()
        lay.addWidget(langWidget)
        lay.addLayout(dbLayout)
        lay.addWidget(self.__doNotAskAgainCheckBox)
        lay.addWidget(self.__notifyFinishCheckBox)
        lay.addWidget(self.__showSecondaryToolBarChkBox)
        lay.addWidget(self.__runAtStartupCheckBox)
        lay.addWidget(self.__manual_updateCheckBox)
        lay.addWidget(self.__manual_UpdateWarning)

        generalGrpBox = QGroupBox(LangClass.TRANSLATIONS["General"])
        generalGrpBox.setLayout(lay)

        self.__maximumMessagesInParameterSpinBox = QSpinBox()
        self.__maximumMessagesInParameterSpinBox.setRange(
            *MAXIMUM_MESSAGES_IN_PARAMETER_RANGE
        )
        self.__maximumMessagesInParameterSpinBox.setValue(
            self.maximum_messages_in_parameter
        )

        self.__show_as_markdown = QCheckBox(LangClass.TRANSLATIONS["Show as Markdown"])
        self.__show_as_markdown.setChecked(self.show_as_markdown)

        lay = QFormLayout()
        lay.addRow(
            LangClass.TRANSLATIONS["Maximum Messages in Parameter"],
            self.__maximumMessagesInParameterSpinBox,
        )
        lay.addRow(self.__show_as_markdown)

        chatBrowserGrpBox = QGroupBox(LangClass.TRANSLATIONS["Chat Browser"])
        chatBrowserGrpBox.setLayout(lay)

        chatColAllCheckBox = QCheckBox(LangClass.TRANSLATIONS["Check All"])
        self.__chatColCheckBoxListWidget = CheckBoxListWidget()
        for k in ChatThreadContainer.get_keys(
            excludes=COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_CHAT
        ):
            self.__chatColCheckBoxListWidget.addItem(
                k, checked=k in self.chat_column_to_show
            )

        chatColAllCheckBox.stateChanged.connect(
            self.__chatColCheckBoxListWidget.toggleState
        )

        lay = QVBoxLayout()
        lay.addWidget(
            QLabel(
                LangClass.TRANSLATIONS[
                    "Select the columns you want to show in the chat list."
                ]
            )
        )
        lay.addWidget(chatColAllCheckBox)
        lay.addWidget(self.__chatColCheckBoxListWidget)

        chatColWidget = QWidget()
        chatColWidget.setLayout(lay)

        imageColAllCheckBox = QCheckBox(LangClass.TRANSLATIONS["Check all"])
        self.__imageColCheckBoxListWidget = CheckBoxListWidget()
        for k in ImagePromptContainer.get_keys(
            excludes=COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_IMAGE
        ):
            self.__imageColCheckBoxListWidget.addItem(
                k, checked=k in self.image_column_to_show
            )

        imageColAllCheckBox.stateChanged.connect(
            self.__imageColCheckBoxListWidget.toggleState
        )

        lay = QVBoxLayout()
        lay.addWidget(
            QLabel(
                LangClass.TRANSLATIONS[
                    "Select the columns you want to show in the image list."
                ]
            )
        )
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
        self.__splitter.setStyleSheet("QSplitterHandle {background-color: lightgray;}")
        self.__splitter.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )

        lay = QVBoxLayout()
        lay.addWidget(self.__splitter)

        columnGrpBox = QGroupBox(LangClass.TRANSLATIONS["Show/hide columns"])
        columnGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(generalGrpBox)
        lay.addWidget(chatBrowserGrpBox)
        lay.addWidget(columnGrpBox)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def getParam(self):
        return {
            "lang": self.__langCmbBox.currentText(),
            "db": self.__dbLineEdit.text(),
            "do_not_ask_again": self.__doNotAskAgainCheckBox.isChecked(),
            "notify_finish": self.__notifyFinishCheckBox.isChecked(),
            "show_secondary_toolbar": self.__showSecondaryToolBarChkBox.isChecked(),
            "chat_column_to_show": COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_CHAT
            + self.__chatColCheckBoxListWidget.getCheckedItemsText(),
            "image_column_to_show": COLUMN_TO_EXCLUDE_FROM_SHOW_HIDE_IMAGE
            + self.__imageColCheckBoxListWidget.getCheckedItemsText(),
            "maximum_messages_in_parameter": self.__maximumMessagesInParameterSpinBox.value(),
            "show_as_markdown": self.__show_as_markdown.isChecked(),
            "run_at_startup": self.__runAtStartupCheckBox.isChecked(),
            "manual_update": self.__manual_updateCheckBox.isChecked(),
        }
