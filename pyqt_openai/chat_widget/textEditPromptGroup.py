from qtpy.QtCore import Signal, QBuffer, QByteArray
from qtpy.QtGui import QTextCursor, QKeySequence
from qtpy.QtWidgets import QVBoxLayout, QWidget, QApplication

from pyqt_openai import PROMPT_BEGINNING_KEY_NAME, PROMPT_MAIN_KEY_NAME, PROMPT_END_KEY_NAME, \
    PROMPT_JSON_KEY_NAME
from pyqt_openai.chat_widget.textEditPrompt import TextEditPrompt
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import moveCursorToOtherPrompt
from pyqt_openai.widgets.jsonEditor import JSONEditor


class TextEditPromptGroup(QWidget):
    textChanged = Signal()
    onUpdateSuggestion = Signal()
    onSendKeySignalToSuggestion = Signal(str)
    onPasteFile = Signal(QByteArray)

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
            # Connect every group text edit widget to the signal
            w.textChanged.connect(self.onUpdateSuggestion)
            w.textChanged.connect(self.textChanged)
            w.moveCursorToOtherPrompt.connect(moveCursorToOtherPrompt)

            # Connect TextEditPrompt signal
            if isinstance(w, TextEditPrompt):
                w.sendSuggestionWidget.connect(self.onSendKeySignalToSuggestion)
            lay.addWidget(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.setVisibleTo(PROMPT_BEGINNING_KEY_NAME, False)
        self.setVisibleTo(PROMPT_JSON_KEY_NAME, False)
        self.setVisibleTo(PROMPT_END_KEY_NAME, False)

        self.__textGroup[PROMPT_MAIN_KEY_NAME].installEventFilter(self)

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
        group_height = 0
        for w in self.__textGroup.values():
            document = w.document()
            height = document.size().height()
            overall_height = int(height+document.documentMargin())
            w.setMaximumHeight(overall_height)
            group_height += overall_height
        return group_height

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

    def eventFilter(self, source, event):
        if event.type() == 6:  # QEvent.KeyPress
            if event.matches(QKeySequence.Paste):
                self.handlePaste()
                return True
        return super().eventFilter(source, event)

    def handlePaste(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = clipboard.image()

            # Save image to a memory buffer
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)

            # Try saving the image as PNG first
            if not image.save(buffer, 'PNG'):
                # If PNG fails, try saving as JPG
                if not image.save(buffer, 'JPG'):
                    # Both formats failed
                    buffer.close()
                    return
                else:
                    image_format = 'JPG'

            buffer.seek(0)
            image_data = buffer.data()
            buffer.close()

            # Emit the image data
            self.onPasteFile.emit(image_data)
        else:
            self.__textEdit.paste()