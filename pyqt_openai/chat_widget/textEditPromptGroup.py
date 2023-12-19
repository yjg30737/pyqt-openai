from qtpy.QtCore import Signal
from qtpy.QtGui import QTextCursor
from qtpy.QtWidgets import QVBoxLayout, QWidget

from pyqt_openai.chat_widget.textEditPrompt import TextEditPrompt
from pyqt_openai.res.language_dict import LangClass


class TextEditPromptGroup(QWidget):
    textChanged = Signal()
    onUpdateSuggestion = Signal()
    onSendKeySignalToSuggestion = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__beginningTextEdit = TextEditPrompt()
        self.__beginningTextEdit.setPlaceholderText(LangClass.TRANSLATIONS['Beginning'])

        self.__textEdit = TextEditPrompt()
        self.__textEdit.setPlaceholderText(LangClass.TRANSLATIONS['Write some text...'])

        self.__endingTextEdit = TextEditPrompt()
        self.__endingTextEdit.setPlaceholderText(LangClass.TRANSLATIONS['Ending'])

        # all false by default
        self.__beginningTextEdit.setVisible(False)
        self.__endingTextEdit.setVisible(False)

        self.__textGroup = [self.__beginningTextEdit, self.__textEdit, self.__endingTextEdit]
        for w in self.__textGroup:
            w.textChanged.connect(self.onUpdateSuggestion)
            w.textChanged.connect(self.textChanged)
            w.sendSuggestionWidget.connect(self.onSendKeySignalToSuggestion)

        lay = QVBoxLayout()
        for w in self.__textGroup:
            lay.addWidget(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

    def executeCommand(self, item, grp):
        command_key = item.text()
        command = ''
        for i in range(len(grp)):
            if grp[i].get('name', '') == command_key:
                command = grp[i].get('value', '')

        w = self.getCurrentTextEdit()
        if w:
            cursor = w.textCursor()
            cursor.deletePreviousChar()
            cursor.select(QTextCursor.WordUnderCursor)
            w.setTextCursor(cursor)
            w.insertPlainText(command)

            self.adjustHeight()

    def getCurrentTextEdit(self):
        for w in self.__textGroup:
            if w.hasFocus():
                return w

    def setCommandEnabled(self, f: bool):
        for w in self.__textGroup:
            w.setCommandSuggestionEnabled(f)

    def adjustHeight(self) -> int:
        """
        adjust overall height of text edit group based on their contents and return adjusted height
        :return:
        """
        groupHeight = 0
        for w in self.__textGroup:
            document = w.document()
            height = document.size().height()
            overallHeight = int(height+document.documentMargin())
            w.setMaximumHeight(overallHeight)
            groupHeight += overallHeight
        return groupHeight

    def getGroup(self):
        return self.__textGroup

    def getContent(self):
        b = self.__textGroup[0].toPlainText().strip()
        m = self.__textGroup[1].toPlainText().strip()
        e = self.__textGroup[2].toPlainText().strip()

        content = ''
        if b:
            content = b + '\n'
        content += m
        if e:
            content += '\n' + e

        return content