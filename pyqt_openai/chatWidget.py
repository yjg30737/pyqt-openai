import json
import os

import requests

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QTextEdit


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

    def showReply(self, content, user_f, stream_f, image_f):
        if image_f:
            self.showImage(content, user_f)
        else:
            self.showText(content, stream_f, user_f)

    def showImage(self, image_url, user_f):
        chatLbl = QLabel()
        response = requests.get(image_url)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        pixmap = pixmap.scaled(chatLbl.width(), chatLbl.height())
        chatLbl.setPixmap(pixmap)
        chatLbl.setStyleSheet('QLabel { background-color: #DDD; padding: 1em }')
        self.widget().layout().addWidget(chatLbl)

    def showText(self, text, stream_f, user_f):
        chatLbl = QLabel(text)
        chatLbl.setWordWrap(True)
        chatLbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if user_f:
            chatLbl.setStyleSheet('QLabel { padding: 1em }')
            chatLbl.setAlignment(Qt.AlignRight)
        else:
            if stream_f:
                lbl = self.widget().layout().itemAt(self.widget().layout().count()-1).widget()
                if isinstance(lbl, QLabel) and lbl.alignment() == Qt.AlignLeft:
                    lbl.setText(lbl.text()+text)
                    return
            chatLbl.setStyleSheet('QLabel { background-color: #DDD; padding: 1em }')
            chatLbl.setAlignment(Qt.AlignLeft)
            chatLbl.setOpenExternalLinks(True)
        self.widget().layout().addWidget(chatLbl)

        conv = {
            'type': 'User' if user_f else 'AI',
            'response': text,
        }

        with open('conv_history.json', 'a') as f:
            f.write(json.dumps(conv) + '\n')


    def event(self, e):
        if e.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(e)

    # TODO distinguish the image response
    def getAllText(self):
        all_text_lst = []
        lay = self.widget().layout()
        if lay:
            for i in range(lay.count()):
                if lay.itemAt(i) and lay.itemAt(i).widget():
                    widget = lay.itemAt(i).widget()
                    if isinstance(widget, QLabel):
                        prefix = 'User' if i % 2 == 0 else 'AI'
                        all_text_lst.append(f'{prefix}: {widget.text()}')

        return '\n'.join(all_text_lst)

    def getLastResponse(self):
        lay = self.widget().layout()
        if lay:
            i = lay.count()-1
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    return widget.text()
        return ''

    def getEveryResponse(self):
        lay = self.widget().layout()
        if lay:
            text_lst = []
            for i in range(lay.count()):
                if lay.itemAt(i) and lay.itemAt(i).widget():
                    widget = lay.itemAt(i).widget()
                    if isinstance(widget, QLabel) and i % 2 == 1:
                        text_lst.append(widget.text())
            return '\n'.join(text_lst)
        else:
            return ''

class TextEditPrompt(QTextEdit):
    returnPressed = Signal()

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


