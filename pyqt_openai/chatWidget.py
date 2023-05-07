import json
import os

import requests

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QPixmap, QFont
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QToolButton, QMenu, QAction, QWidget, QLabel, QHBoxLayout, QTextEdit, QStackedWidget

from pyqt_openai.svgToolButton import SvgToolButton


class ChatBrowser(QScrollArea):
    convUnitUpdated = Signal(int, int, str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__cur_id = 0

    def __initUi(self):
        self.__homeWidget = QLabel('Home')
        self.__homeWidget.setAlignment(Qt.AlignCenter)
        self.__homeWidget.setFont(QFont('Arial', 32))

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__chatWidget = QWidget()
        self.__chatWidget.setLayout(lay)

        widget = QStackedWidget()
        widget.addWidget(self.__homeWidget)
        widget.addWidget(self.__chatWidget)
        self.setWidget(widget)
        self.setWidgetResizable(True)

    def getChatWidget(self):
        return self.__chatWidget

    def showLabel(self, text, user_f, stream_f, image_f):
        if image_f:
            self.showImage(text, user_f)
        else:
            self.showText(text, stream_f, user_f)
        if not stream_f:
            # change user_f type from bool to int to insert in db
            self.convUnitUpdated.emit(self.__cur_id, int(user_f), text)

    def streamFinished(self):
        self.convUnitUpdated.emit(self.__cur_id, 0, self.getLastResponse())

    def showImage(self, image_url, user_f):
        chatLbl = QLabel()
        response = requests.get(image_url)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        pixmap = pixmap.scaled(chatLbl.width(), chatLbl.height())
        chatLbl.setPixmap(pixmap)
        chatLbl.setStyleSheet('QLabel { background-color: #DDD; padding: 1em }')
        self.getChatWidget().layout().addWidget(chatLbl)

    def showText(self, text, stream_f, user_f):
        if self.widget().currentWidget() == self.__chatWidget:
            pass
        else:
            self.widget().setCurrentIndex(1)
        self.__setLabel(text, stream_f, user_f)

    def __setLabel(self, text, stream_f, user_f):
        chatLbl = QLabel(text)
        chatLbl.setWordWrap(True)
        chatLbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if user_f:
            chatLbl.setStyleSheet('QLabel { padding: 1em }')
            chatLbl.setAlignment(Qt.AlignRight)
        else:
            if stream_f:
                lbl = self.getChatWidget().layout().itemAt(self.getChatWidget().layout().count()-1).widget()
                if isinstance(lbl, QLabel) and lbl.alignment() == Qt.AlignLeft:
                    lbl.setText(lbl.text()+text)
                    return
            chatLbl.setStyleSheet('QLabel { background-color: #DDD; padding: 1em }')
            chatLbl.setAlignment(Qt.AlignLeft)
            chatLbl.setOpenExternalLinks(True)
        self.getChatWidget().layout().addWidget(chatLbl)

    def event(self, e):
        if e.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(e)

    # TODO distinguish the image response
    def getAllText(self):
        all_text_lst = []
        lay = self.getChatWidget().layout()
        if lay:
            for i in range(lay.count()):
                if lay.itemAt(i) and lay.itemAt(i).widget():
                    widget = lay.itemAt(i).widget()
                    if isinstance(widget, QLabel):
                        prefix = 'User' if i % 2 == 0 else 'AI'
                        all_text_lst.append(f'{prefix}: {widget.text()}')

        return '\n'.join(all_text_lst)

    def getLastResponse(self):
        lay = self.getChatWidget().layout()
        if lay:
            i = lay.count()-1
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    return widget.text()
        return ''

    def getEveryResponse(self):
        lay = self.getChatWidget().layout()
        if lay:
            text_lst = []
            for i in range(lay.count()):
                item = lay.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QLabel) and i % 2 == 1:
                        text_lst.append(widget.text())
            return '\n'.join(text_lst)
        else:
            return ''

    def clear(self):
        lay = self.getChatWidget().layout()
        if lay:
            for i in range(lay.count()-1, -1, -1):
                item = lay.itemAt(i)
                if item and item.widget():
                    lay.removeWidget(item.widget())
        self.widget().setCurrentIndex(0)

    def isNew(self):
        return self.widget().currentIndex() == 0

    def setCurId(self, id):
        self.__cur_id = id

    def resetChatWidget(self, id):
        self.clear()
        self.setCurId(id)

    def replaceConv(self, id, conv_data):
        self.clear()
        self.setCurId(id)
        self.widget().setCurrentIndex(1)
        for i in range(len(conv_data)):
            self.__setLabel(conv_data[i], False, not bool(i % 2))


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


class TextEditPropmtGroup(QWidget):
    textChanged = Signal()

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__beginningTextEdit = TextEditPrompt()
        self.__beginningTextEdit.textChanged.connect(self.textChanged)
        self.__beginningTextEdit.setPlaceholderText('Beginning')

        self.__textEdit = TextEditPrompt()
        self.__textEdit.textChanged.connect(self.textChanged)
        self.__textEdit.setPlaceholderText('Write some text...')

        self.__endingTextEdit = TextEditPrompt()
        self.__endingTextEdit.textChanged.connect(self.textChanged)
        self.__endingTextEdit.setPlaceholderText('Ending')

        self.__beginningTextEdit.setVisible(False)
        self.__endingTextEdit.setVisible(False)

        self.__textGroup = [self.__beginningTextEdit, self.__textEdit, self.__endingTextEdit]

        lay = QVBoxLayout()
        for w in self.__textGroup:
            lay.addWidget(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

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

class Prompt(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__textEditGroup = TextEditPropmtGroup()
        self.__textEditGroup.textChanged.connect(self.updateHeight)

        settingsBtn = SvgToolButton()
        settingsBtn.setIcon('ico/vertical_three_dots.svg')
        settingsBtn.setToolTip('Prompt Settings')

        # Create the menu
        menu = QMenu(self)

        # Create the actions
        beginningAction = QAction("Show Beginning", self)
        beginningAction.setCheckable(True)
        beginningAction.toggled.connect(self.__showBeginning)
        endingAction = QAction("Show Ending", self)
        endingAction.setCheckable(True)
        endingAction.toggled.connect(self.__showEnding)

        # Add the actions to the menu
        menu.addAction(beginningAction)
        menu.addAction(endingAction)

        # Connect the button to the menu
        settingsBtn.setMenu(menu)
        settingsBtn.setPopupMode(QToolButton.InstantPopup)

        lay = QVBoxLayout()
        lay.addWidget(settingsBtn)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setAlignment(Qt.AlignBottom)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(self.__textEditGroup)
        lay.addWidget(rightWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setLayout(lay)
        self.updateHeight()

    def updateHeight(self):
        overallHeight = self.__textEditGroup.adjustHeight()
        self.setMaximumHeight(overallHeight)

    def getTextEdit(self):
        return self.__textEditGroup.getGroup()[1]

    def getContent(self):
        return self.__textEditGroup.getContent()

    def __showBeginning(self, f):
        self.__textEditGroup.getGroup()[0].setVisible(f)

    def __showEnding(self, f):
        self.__textEditGroup.getGroup()[-1].setVisible(f)



