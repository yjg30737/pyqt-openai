from qtpy.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel

from pyqt_openai.res.language_dict import LangClass


class CommandSuggestionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__commandList = QListWidget()
        self.__commandList.currentRowChanged.connect(self.onCountChanged)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Command List']))
        lay.addWidget(self.__commandList)
        lay.setContentsMargins(0, 5, 0, 0)

        self.setLayout(lay)

    def getCommandList(self):
        return self.__commandList

    def onCountChanged(self):
        itemHeight = self.__commandList.sizeHintForRow(0)
        itemCount = self.__commandList.count()
        contentHeight = itemHeight * itemCount
        scrollbarHeight = self.__commandList.verticalScrollBar().sizeHint().height()
        totalHeight = contentHeight + itemHeight
        self.setMaximumHeight(totalHeight + scrollbarHeight)