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

    def __initUi(self):
        self.setStyleSheet('QTextEdit { border: 1px solid #AAA; } ')

    def setCommandSuggestionEnabled(self, f):
        self.__commandSuggestionEnabled = f

    def keyPressEvent(self, e):
        if self.__commandSuggestionEnabled:
            if e.key() == Qt.Key_Up:
                self.sendSuggestionWidget.emit('up')
            elif e.key() == Qt.Key_Down:
                self.sendSuggestionWidget.emit('down')

        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            if e.modifiers() == Qt.ShiftModifier:
                return super().keyPressEvent(e)
            else:
                if self.__commandSuggestionEnabled:
                    self.sendSuggestionWidget.emit('enter')
                else:
                    self.returnPressed.emit()
        else:
            return super().keyPressEvent(e)