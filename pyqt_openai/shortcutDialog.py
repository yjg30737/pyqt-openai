from PySide6.QtWidgets import QLabel, QFormLayout, QGroupBox, QDialog

from pyqt_openai import (
    DEFAULT_SHORTCUT_FIND_PREV,
    DEFAULT_SHORTCUT_FIND_NEXT,
    DEFAULT_SHORTCUT_PROMPT_BEGINNING,
    DEFAULT_SHORTCUT_PROMPT_ENDING,
    DEFAULT_SHORTCUT_SUPPORT_PROMPT_COMMAND,
    DEFAULT_SHORTCUT_FULL_SCREEN,
    DEFAULT_SHORTCUT_FIND,
    DEFAULT_SHORTCUT_JSON_MODE,
    DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW,
    DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW,
    DEFAULT_SHORTCUT_CONTROL_PROMPT_WINDOW,
    DEFAULT_SHORTCUT_SETTING,
    DEFAULT_SHORTCUT_SEND,
    DEFAULT_SHORTCUT_SHOW_SECONDARY_TOOLBAR,
    DEFAULT_SHORTCUT_FOCUS_MODE,
)
from pyqt_openai.lang.translations import LangClass


class ShortcutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__shortcuts = {
            "SHORTCUT_FIND_PREV": {
                "label": f"{LangClass.TRANSLATIONS['Find']} - {LangClass.TRANSLATIONS['Previous']}",
                "value": DEFAULT_SHORTCUT_FIND_PREV,
            },
            "SHORTCUT_FIND_NEXT": {
                "label": f"{LangClass.TRANSLATIONS['Find']} - {LangClass.TRANSLATIONS['Next']}",
                "value": DEFAULT_SHORTCUT_FIND_NEXT,
            },
            "SHORTCUT_PROMPT_BEGINNING": {
                "label": LangClass.TRANSLATIONS["Prompt Beginning"],
                "value": DEFAULT_SHORTCUT_PROMPT_BEGINNING,
            },
            "SHORTCUT_PROMPT_ENDING": {
                "label": LangClass.TRANSLATIONS["Prompt Ending"],
                "value": DEFAULT_SHORTCUT_PROMPT_ENDING,
            },
            "SHORTCUT_SUPPORT_PROMPT_COMMAND": {
                "label": LangClass.TRANSLATIONS["Support Prompt Command"],
                "value": DEFAULT_SHORTCUT_SUPPORT_PROMPT_COMMAND,
            },
            "SHOW_SECONDARY_TOOLBAR": {
                "label": LangClass.TRANSLATIONS["Show Secondary Toolbar"],
                "value": DEFAULT_SHORTCUT_SHOW_SECONDARY_TOOLBAR,
            },
            "SHORTCUT_FOCUS_MODE": {
                "label": LangClass.TRANSLATIONS["Focus Mode"],
                "value": DEFAULT_SHORTCUT_FOCUS_MODE,
            },
            "SHORTCUT_FULL_SCREEN": {
                "label": LangClass.TRANSLATIONS["Full Screen"],
                "value": DEFAULT_SHORTCUT_FULL_SCREEN,
            },
            "SHORTCUT_FIND": {
                "label": LangClass.TRANSLATIONS["Find"],
                "value": DEFAULT_SHORTCUT_FIND,
            },
            "SHORTCUT_JSON_MODE": {
                "label": LangClass.TRANSLATIONS["JSON Mode"],
                "value": DEFAULT_SHORTCUT_JSON_MODE,
            },
            "SHORTCUT_LEFT_SIDEBAR_WINDOW": {
                "label": LangClass.TRANSLATIONS["Left Sidebar Window"],
                "value": DEFAULT_SHORTCUT_LEFT_SIDEBAR_WINDOW,
            },
            "SHORTCUT_RIGHT_SIDEBAR_WINDOW": {
                "label": LangClass.TRANSLATIONS["Right Sidebar Window"],
                "value": DEFAULT_SHORTCUT_RIGHT_SIDEBAR_WINDOW,
            },
            "SHORTCUT_CONTROL_PROMPT_WINDOW": {
                "label": LangClass.TRANSLATIONS["Control Prompt Window"],
                "value": DEFAULT_SHORTCUT_CONTROL_PROMPT_WINDOW,
            },
            "SHORTCUT_SETTING": {
                "label": LangClass.TRANSLATIONS["Setting"],
                "value": DEFAULT_SHORTCUT_SETTING,
            },
            "SHORTCUT_SEND": {
                "label": LangClass.TRANSLATIONS["Send"],
                "value": DEFAULT_SHORTCUT_SEND,
            },
        }
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["Shortcuts"])

        lay = QFormLayout()

        shortcutGroupBox = QGroupBox(LangClass.TRANSLATIONS["Shortcuts"])
        shortcutGroupBox.setLayout(lay)

        for key, shortcut in self.__shortcuts.items():
            lineEdit = QLabel()
            lineEdit.setText(shortcut["value"])
            shortcut["lineEdit"] = lineEdit
            lay.addRow(shortcut["label"], lineEdit)

        self.setLayout(lay)
