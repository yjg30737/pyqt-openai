from qtpy.QtCore import Signal
from qtpy.QtGui import QTextCursor
from qtpy.QtWidgets import QVBoxLayout, QWidget

from pyqt_openai.chat_widget.textEditPrompt import TextEditPrompt
from pyqt_openai.constants import PROMPT_BEGINNING_KEY_NAME, PROMPT_MAIN_KEY_NAME, PROMPT_END_KEY_NAME, \
    PROMPT_JSON_KEY_NAME
from pyqt_openai.chat_widget.jsonTextEdit import JSONEditor
from pyqt_openai.lang.translations import LangClass


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

        self.__jsonTextEdit = JSONEditor()

        # Grouping text edit widgets for easy access and management
        self.__textGroup = {
            PROMPT_BEGINNING_KEY_NAME: self.__beginningTextEdit,
            PROMPT_MAIN_KEY_NAME: self.__textEdit,
            PROMPT_JSON_KEY_NAME: self.__jsonTextEdit,
            PROMPT_END_KEY_NAME: self.__endingTextEdit
        }

        lay = QVBoxLayout()
        for w in self.__textGroup.values():
            w.textChanged.connect(self.onUpdateSuggestion)
            w.textChanged.connect(self.textChanged)
            if isinstance(w, TextEditPrompt):
                w.sendSuggestionWidget.connect(self.onSendKeySignalToSuggestion)
            lay.addWidget(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.setVisibleTo(PROMPT_BEGINNING_KEY_NAME, False)
        self.setVisibleTo(PROMPT_JSON_KEY_NAME, False)
        self.setVisibleTo(PROMPT_END_KEY_NAME, False)

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
        for w in self.__textGroup.values():
            if w.hasFocus():
                return w

    def setCommandEnabled(self, f: bool):
        for w in self.__textGroup.values():
            if isinstance(w, TextEditPrompt):
                w.setCommandSuggestionEnabled(f)

    def adjustHeight(self) -> int:
        """
        Adjust overall height of text edit group based on their contents and return adjusted height
        """
        groupHeight = 0
        for w in self.__textGroup.values():
            document = w.document()
            height = document.size().height()
            overallHeight = int(height+document.documentMargin())
            w.setMaximumHeight(overallHeight)
            groupHeight += overallHeight
        return groupHeight

    def setVisibleTo(self, key, f):
        if key in self.__textGroup:
            self.__textGroup[key].setVisible(f)

    def getContent(self):
        b = self.__textGroup[PROMPT_BEGINNING_KEY_NAME].toPlainText().strip()
        m = self.__textGroup[PROMPT_MAIN_KEY_NAME].toPlainText().strip()
        e = self.__textGroup[PROMPT_END_KEY_NAME].toPlainText().strip()

        content = ''
        if b:
            content = b + '\n'
        content += m
        if e:
            content += '\n' + e

        return content

    def getJSONContent(self):
        j = self.__textGroup[PROMPT_JSON_KEY_NAME].toPlainText().strip()
        return j

    def getMainTextEdit(self):
        return self.__textEdit

    def getGroup(self):
        """
        Get the text group.
        These are only used when you need to handle widgets in the group in detail.
        """
        return self.__textGroup

