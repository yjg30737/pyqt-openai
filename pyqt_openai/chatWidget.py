from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QTextEdit


class ChatBrowser(QScrollArea):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        widget = QWidget()
        widget.setLayout(lay)
        self.setWidget(widget)
        self.setWidgetResizable(True)

    def showText(self, text, user_f):
        chatLbl = QLabel(text)
        chatLbl.setWordWrap(True)
        chatLbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if user_f:
            chatLbl.setStyleSheet('QLabel { padding: 1em }')
            chatLbl.setAlignment(Qt.AlignRight)
        else:
            chatLbl.setStyleSheet('QLabel { background-color: #DDD; padding: 1em }')
            chatLbl.setAlignment(Qt.AlignLeft)
        self.widget().layout().addWidget(chatLbl)

    def event(self, e):
        if e.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(e)


class TextEditPrompt(QTextEdit):
    returnPressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initUi()

    def __initUi(self):
        self.setStyleSheet('QTextEdit { border: 1px solid #AAA; } ')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            if e.modifiers() == Qt.ShiftModifier:
                return super().keyPressEvent(e)
            else:
                self.returnPressed.emit()
        else:
            return super().keyPressEvent(e)


class Prompt(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__textEdit = TextEditPrompt()
        self.__textEdit.textChanged.connect(self.updateHeight)
        lay = QHBoxLayout()
        lay.addWidget(self.__textEdit)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)
        self.updateHeight()

    def updateHeight(self):
        document = self.__textEdit.document()
        height = document.size().height()
        self.setMaximumHeight(int(height+document.documentMargin()))

    def getTextEdit(self):
        return self.__textEdit


