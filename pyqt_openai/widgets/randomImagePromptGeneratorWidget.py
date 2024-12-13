from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCheckBox, QGroupBox, QLabel, QListWidgetItem, QVBoxLayout, QWidget

from pyqt_openai import RANDOMIZING_PROMPT_SOURCE_ARR
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget


class RandomImagePromptGeneratorWidget(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # TODO LANGUAGE
        self.setWindowTitle("Random Sentence Generator")

        lbl = QLabel("Select the elements you want to include in the prompt")

        self.__allCheckBox: QCheckBox = QCheckBox(LangClass.TRANSLATIONS["Select All"])

        self.__listWidget: CheckBoxListWidget = CheckBoxListWidget()

        for e in RANDOMIZING_PROMPT_SOURCE_ARR:
            item = QListWidgetItem(", ".join(e))
            item.setFlags(
                item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEditable,
            )
            item.setCheckState(Qt.CheckState.Unchecked)
            self.__listWidget.addItem(item)

        lay = QVBoxLayout()
        lay.addWidget(lbl)
        lay.addWidget(self.__allCheckBox)
        lay.addWidget(self.__listWidget)

        self.__randomPromptGroup: QGroupBox = QGroupBox()
        self.__randomPromptGroup.setTitle("List of random words to generate a prompt")
        self.__randomPromptGroup.setLayout(lay)

        useBtn = QCheckBox("Use random-generated prompt")
        useBtn.toggled.connect(self.__toggleRandomPrompt)

        lay = QVBoxLayout()
        lay.addWidget(useBtn)
        lay.addWidget(self.__randomPromptGroup)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self.__allCheckBox.stateChanged.connect(
            self.__listWidget.toggleState,
        )  # if allChkBox is checked, tablewidget checkboxes will also be checked
        self.__randomPromptGroup.setVisible(False)

    def isRandomPromptEnabled(self):
        return self.__randomPromptGroup.isVisible()

    def __toggleRandomPrompt(self, f: bool):
        self.__randomPromptGroup.setVisible(f)
        self.__allCheckBox.setChecked(f)

    def getRandomPromptSourceArr(self) -> list[list[str]] | None:
        return (
            [t.split(", ") for t in self.__listWidget.getCheckedItemsText()]
            if self.isRandomPromptEnabled()
            else None
        )
