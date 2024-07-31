from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QTextEdit


class TextEditPrompt(QTextEdit):
    returnPressed = Signal()
    sendSuggestionWidget = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__commandSuggestionEnabled = False
        self.__executeEnabled = True

    def __initUi(self):
        self.setAcceptRichText(False)

    def setExecuteEnabled(self, f):
        self.__executeEnabled = f

    def setCommandSuggestionEnabled(self, f):
        self.__commandSuggestionEnabled = f

    def sendMessage(self):
        self.returnPressed.emit()

    def keyPressEvent(self, e):
        # Send key events to the suggestion widget if enabled
        if self.__commandSuggestionEnabled:
            if e.key() == Qt.Key.Key_Up:
                self.sendSuggestionWidget.emit('up')
            elif e.key() == Qt.Key.Key_Down:
                self.sendSuggestionWidget.emit('down')
        if (e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter) and self.__executeEnabled:
            if e.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                return super().keyPressEvent(e)
            else:
                if self.__commandSuggestionEnabled:
                    self.sendSuggestionWidget.emit('enter')
                else:
                    self.sendMessage()
        else:
            return super().keyPressEvent(e)