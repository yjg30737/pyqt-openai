from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QSplitter,
)

from pyqt_openai.chat_widget.prompt_gen_widget.promptGroupList import PromptGroupList
from pyqt_openai.chat_widget.prompt_gen_widget.promptTable import PromptTable
from pyqt_openai.globals import DB


class PromptPage(QWidget):
    updated = Signal(str)

    def __init__(self, prompt_type='form', parent=None):
        super().__init__(parent)
        self.__initVal(prompt_type)
        self.__initUi()

    def __initVal(self, prompt_type):
        self.prompt_type = prompt_type
        self.__groups = DB.selectPromptGroup(prompt_type=self.prompt_type)

    def __initUi(self):
        leftWidget = PromptGroupList(prompt_type=self.prompt_type)
        leftWidget.added.connect(self.add)
        leftWidget.deleted.connect(self.delete)

        leftWidget.currentRowChanged.connect(self.__showEntries)

        self.__table = PromptTable()
        if len(self.__groups) > 0:
            leftWidget.list.setCurrentRow(0)
            self.__table.showEntries(self.__groups[0].id)
        self.__table.updated.connect(self.updated)

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(self.__table)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)

        self.setLayout(lay)

    def add(self, id):
        self.__table.showEntries(id)

    def delete(self, id):
        if self.__table.getId() == id:
            self.__table.setNothingRightNow()
        elif len(DB.selectPromptGroup(prompt_type=self.prompt_type)) == 0:
            self.__table.setNothingRightNow()

    def __showEntries(self, id):
        self.__table.showEntries(id)
