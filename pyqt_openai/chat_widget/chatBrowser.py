import re
from typing import List

from qtpy.QtGui import QTextCharFormat, QColor, QTextCursor
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel

from pyqt_openai import MAXIMUM_MESSAGES_IN_PARAMETER
from pyqt_openai.chat_widget.aiChatUnit import AIChatUnit
from pyqt_openai.chat_widget.userChatUnit import UserChatUnit
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.util.script import is_valid_regex


class ChatBrowser(QScrollArea):
    messageUpdated = Signal(ChatMessageContainer)
    onReplacedCurrentPage = Signal(int)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__cur_id = 0

        self.__user_image = ''
        self.__ai_image = ''

    def __initUi(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__chatWidget = QWidget()
        self.__chatWidget.setLayout(lay)

        self.setWidget(self.__chatWidget)
        self.setWidgetResizable(True)

    def showLabel(self, text, stream_f, arg: ChatMessageContainer):
        arg.thread_id = arg.thread_id if arg.thread_id else self.__cur_id
        unit = self.__setLabel(text, stream_f, arg.role)
        if not stream_f:
            arg.id = DB.insertMessage(arg)
            self.__showConvResultInfo(unit, arg)

    def showLabelForFavorite(self, arg: ChatMessageContainer):
        unit = self.__setLabel(arg.content, False, arg.role)
        self.__showConvResultInfo(unit, arg)

    def __getLastUnit(self) -> AIChatUnit | None:
        item = self.widget().layout().itemAt(self.widget().layout().count() - 1)
        if item:
            return item.widget()
        else:
            return None

    def __showConvResultInfo(self, unit, arg: ChatMessageContainer):
        if isinstance(unit, AIChatUnit):
            unit.afterResponse(arg)

    def streamFinished(self, arg: ChatMessageContainer):
        unit = self.__getLastUnit()
        arg.content = self.getLastResponse()
        arg.id = DB.insertMessage(arg)
        self.__showConvResultInfo(unit, arg)

    def __setLabel(self, text, stream_f, role):
        chatUnit = QLabel()
        if role == 'user':
            chatUnit = UserChatUnit()
            chatUnit.setText(text)
            chatUnit.setIcon(self.__user_image)
        else:
            chatUnit = AIChatUnit()
            if chatUnit.getIcon():
                pass
            else:
                chatUnit.setIcon(self.__ai_image)
            if stream_f:
                unit = self.__getLastUnit()
                if isinstance(unit, AIChatUnit):
                    # TODO 2023-11-10
                    unit.toggleGUI(False)
                    unit.addText(text)
                    return
            chatUnit.setText(text)

        self.widget().layout().addWidget(chatUnit)
        return chatUnit

    def event(self, event):
        if event.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(event)

    def getMessages(self, limit=MAXIMUM_MESSAGES_IN_PARAMETER):
        messages = DB.selectCertainThreadMessages(self.__cur_id)
        all_text_lst = [{
            'role': message.role,
            'content': message.content
        } for message in messages]
        all_text_lst = all_text_lst[-limit:]

        return all_text_lst

    def getLastResponse(self):
        lay = self.widget().layout()
        if lay:
            i = lay.count()-1
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, AIChatUnit):
                    return widget.text()
        return ''

    def getEveryResponse(self):
        lay = self.widget().layout()
        if lay:
            text_lst = []
            for i in range(lay.count()):
                item = lay.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, AIChatUnit) and i % 2 == 1:
                        text_lst.append(widget.text())
            return '\n'.join(text_lst)
        else:
            return ''

    def clear(self):
        """
        This method is used to clear the chat widget, not the database.
        """
        lay = self.widget().layout()
        if lay:
            for i in range(lay.count()-1, -1, -1):
                item = lay.itemAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
        self.onReplacedCurrentPage.emit(0)

    def setCurId(self, id):
        self.__cur_id = id

    def getCurId(self):
        return self.__cur_id

    def resetChatWidget(self, id):
        self.clear()
        self.setCurId(id)

    def __getEveryLabels(self):
        lay = self.widget().layout()
        labels = [lay.itemAt(i).widget() for i in range(lay.count()) if lay.itemAt(i)]
        return labels

    def __getEveryUserLabels(self):
        lay = self.widget().layout()
        labels = [lay.itemAt(i).widget() for i in range(lay.count()) if lay.itemAt(i) and isinstance(lay.itemAt(i).widget(), UserChatUnit)]
        return labels

    def __getEveryAILabels(self):
        lay = self.widget().layout()
        labels = [lay.itemAt(i).widget() for i in range(lay.count()) if lay.itemAt(i) and isinstance(lay.itemAt(i).widget(), AIChatUnit)]
        return labels

    def getLastFinishReason(self):
        # TODO 2023-11-11
        # 1 is continue 0 is not continue
        return 1

    def clearFormatting(self, label):
        cursor = label.textCursor()
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        cursor.setCharFormat(format)

    def highlightText(self, label, pattern, case_sensitive, word_only):
        self.clearFormatting(label)  # Clear any previous formatting

        cursor = label.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor("yellow"))
        format.setForeground(QColor("blue"))

        # Ensure we start from the beginning
        cursor.setPosition(0)

        # Create regex pattern for word-only search if needed
        if word_only:
            pattern = r'\b' + re.escape(pattern) + r'\b'

        # Find and highlight all occurrences of the pattern
        regex_flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, regex_flags)
        text = label.toPlainText()

        for match in regex.finditer(text):
            start, end = match.span()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format)

    def setCurrentLabelIncludingTextBySliderPosition(self, text, case_sensitive=False, word_only=False, is_regex=False):
        labels = self.__getEveryLabels()
        label_info = [{'class':label.getLbl(), 'text':label.toPlainText(), 'pos':label.y()} for label in labels]
        res_lbl = []

        for _ in label_info:
            pattern = text
            if is_regex:
                if is_valid_regex(pattern):
                    if case_sensitive:
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            res_lbl.append(_)
                            self.highlightText(_['class'], pattern, case_sensitive, word_only)
                    else:
                        result = re.search(pattern, _['text'])
                        if result:
                            res_lbl.append(_)
                            self.highlightText(_['class'], pattern, case_sensitive, word_only)
                else:
                    if _['text'].find(text) != -1:
                        res_lbl.append(_)
                        self.highlightText(_['class'], pattern, case_sensitive, word_only)
            else:
                if case_sensitive:
                    if word_only:
                        pattern = r'\b' + re.escape(text) + r'\b'
                        result = re.search(pattern, _['text'])
                        if result:
                            res_lbl.append(_)
                            self.highlightText(_['class'], pattern, case_sensitive, word_only)
                    else:
                        if _['text'].find(text) != -1:
                            res_lbl.append(_)
                            self.highlightText(_['class'], pattern, case_sensitive, word_only)
                else:
                    if word_only:
                        pattern = r'\b' + re.escape(text) + r'\b'
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            res_lbl.append(_)
                            self.highlightText(_['class'], pattern, case_sensitive, word_only)
                    else:
                        pattern = re.escape(text)
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            res_lbl.append(_)
                            self.highlightText(_['class'], pattern, case_sensitive, word_only)

        return res_lbl

    def replaceThread(self, args: List[ChatMessageContainer], id):
        """
        For showing messages from the thread
        """
        self.clear()
        self.setCurId(id)
        self.onReplacedCurrentPage.emit(1)
        for i in range(len(args)):
            arg = args[i]
            # stream is False no matter what
            unit = self.__setLabel(arg.content, False, arg.role)
            self.__showConvResultInfo(unit, arg)

    def replaceThreadForFavorite(self, args: List[ChatMessageContainer]):
        """
        For showing favorite messages
        """
        self.clear()
        self.onReplacedCurrentPage.emit(1)
        for i in range(len(args)):
            arg = args[i]
            # stream is False no matter what
            unit = self.__setLabel(arg.content, False, arg.role)
            self.__showConvResultInfo(unit, arg)

    def setUserImage(self, img):
        self.__user_image = img
        lbls = self.__getEveryUserLabels()
        for lbl in lbls:
            lbl.setIcon(img)

    def setAIImage(self, img):
        self.__ai_image = img
        lbls = self.__getEveryAILabels()
        for lbl in lbls:
            lbl.setIcon(img)