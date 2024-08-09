from qtpy.QtWidgets import QWidget, QCheckBox, QFormLayout

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import SettingsParamsContainer


class ShortcutSettingsWidget(QWidget):
    def __init__(self, args: SettingsParamsContainer, parent=None):
        super().__init__(parent)
        self.__initVal(args)
        self.__initUi()

    def __initVal(self, args):
        self.__args = args

    def __initUi(self):
        self.__showAsMarkdownCheckBox = QCheckBox()
        self.__showAsMarkdownCheckBox.setChecked(self.__args.show_as_markdown)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS['Show as Markdown'], self.__showAsMarkdownCheckBox)

        self.setLayout(lay)

    def getParam(self):
        return {
            'show_as_markdown': self.__showAsMarkdownCheckBox.isChecked()
        }