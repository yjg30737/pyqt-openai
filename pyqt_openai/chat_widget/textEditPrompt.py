from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QTextEdit


class TextEditPrompt(QTextEdit):
    returnPressed = Signal()
    sendSuggestionWidget = Signal(str)
    moveCursorToOtherPrompt = Signal(str)

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

    def keyPressEvent(self, event):
        # Send key events to the suggestion widget if enabled
        if self.__commandSuggestionEnabled:
            if event.key() == Qt.Key.Key_Up:
                self.sendSuggestionWidget.emit('up')
            elif event.key() == Qt.Key.Key_Down:
                self.sendSuggestionWidget.emit('down')
        else:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Up:
                    self.moveCursorToOtherPrompt.emit('up')
                    return
                elif event.key() == Qt.Key.Key_Down:
                    self.moveCursorToOtherPrompt.emit('down')
                    return
                else:
                    return super().keyPressEvent(event)

        if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and self.__executeEnabled:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                return super().keyPressEvent(event)
            else:
                if self.__commandSuggestionEnabled:
                    self.sendSuggestionWidget.emit('enter')
                else:
                    self.sendMessage()
        else:
            return super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.setCursorWidth(1)
        return super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setCursorWidth(0)
        return super().focusInEvent(event)