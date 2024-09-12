from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QListWidgetItem, \
    QLabel, QCheckBox, QGroupBox

from pyqt_openai import RANDOMIZING_PROMPT_SOURCE_ARR
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import generate_random_prompt
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget


class RandomImagePromptGeneratorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__randomizing_prompt_source_arr = RANDOMIZING_PROMPT_SOURCE_ARR
        self.__initUi()

    def __initUi(self):
        # TODO LANGUAGE
        self.setWindowTitle('Random Sentence Generator')

        lbl = QLabel('Select the elements you want to include in the prompt')

        self.__allCheckBox = QCheckBox(LangClass.TRANSLATIONS['Select All'])

        self.__listWidget = CheckBoxListWidget()

        for e in self.__randomizing_prompt_source_arr:
            item = QListWidgetItem(', '.join(e))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.__listWidget.addItem(item)

        lay = QVBoxLayout()
        lay.addWidget(lbl)
        lay.addWidget(self.__allCheckBox)
        lay.addWidget(self.__listWidget)

        self.__randomPromptGroup = QGroupBox()
        self.__randomPromptGroup.setTitle('List of random words to generate a prompt')
        self.__randomPromptGroup.setLayout(lay)

        useBtn = QCheckBox('Use random-generated prompt')
        useBtn.toggled.connect(self.__toggleRandomPrompt)

        lay = QVBoxLayout()
        lay.addWidget(useBtn)
        lay.addWidget(self.__randomPromptGroup)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self.__allCheckBox.stateChanged.connect(self.__listWidget.toggleState) # if allChkBox is checked, tablewidget checkboxes will also be checked
        self.__randomPromptGroup.setVisible(False)

    # TODO CONFIG
    def isRandomPromptEnabled(self):
        return self.__randomPromptGroup.isVisible()

    def __toggleRandomPrompt(self, f):
        self.__randomPromptGroup.setVisible(f)
        self.__allCheckBox.setChecked(f)

    def getRandomPromptSourceArr(self):
        self.__randomizing_prompt_source_arr = [t.split(', ') for t in self.__listWidget.getCheckedItemsText()]
        return self.__randomizing_prompt_source_arr
