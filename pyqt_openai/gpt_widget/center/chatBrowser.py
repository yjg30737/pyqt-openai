import re
from typing import List

from qtpy.QtGui import QTextCharFormat, QColor, QTextCursor
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel

from pyqt_openai import MAXIMUM_MESSAGES_IN_PARAMETER, DEFAULT_FOUND_TEXT_BG_COLOR, DEFAULT_FOUND_TEXT_COLOR
from pyqt_openai.gpt_widget.center.aiChatUnit import AIChatUnit
from pyqt_openai.gpt_widget.center.userChatUnit import UserChatUnit
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
            self.__setResponseInfo(unit, arg)

    def showLabelForFavorite(self, arg: ChatMessageContainer):
        unit = self.__setLabel(arg.content, False, arg.role)
        self.__setResponseInfo(unit, arg)

    def __getLastUnit(self) -> AIChatUnit | None:
        item = self.widget().layout().itemAt(self.widget().layout().count() - 1)
        if item:
            return item.widget()
        else:
            return None

    def __setResponseInfo(self, unit, arg: ChatMessageContainer):
        if isinstance(unit, AIChatUnit):
            unit.afterResponse(arg)

    def streamFinished(self, arg: ChatMessageContainer):
        unit = self.__getLastUnit()
        arg.content = self.getLastResponse()
        arg.id = DB.insertMessage(arg)
        self.__setResponseInfo(unit, arg)

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
                    return widget.getText()
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

    def __getLabelsByType(self, label_type=None):
        """
        Retrieve all labels from the widget's layout, optionally filtering by a specific label type.

        :param label_type: The type of label to filter by (e.g., UserChatUnit, AIChatUnit). If None, retrieves all labels.
        :return: A list of label widgets.
        """
        lay = self.widget().layout()
        labels = []
        for i in range(lay.count()):
            item = lay.itemAt(i)
            if item:
                widget = item.widget()
                if label_type is None or isinstance(widget, label_type):
                    labels.append(widget)
        return labels

    def __getEveryLabels(self):
        """
        Retrieve all labels from the widget's layout.

        :return: A list of all label widgets.
        """
        return self.__getLabelsByType()

    def __getEveryUserLabels(self):
        """
        Retrieve all user-specific labels from the widget's layout.

        :return: A list of UserChatUnit label widgets.
        """
        return self.__getLabelsByType(UserChatUnit)

    def __getEveryAILabels(self):
        """
        Retrieve all AI-specific labels from the widget's layout.

        :return: A list of AIChatUnit label widgets.
        """
        return self.__getLabelsByType(AIChatUnit)

    def isFinishedByLength(self):
        return self.__getLastUnit().getResponseInfo().finish_reason == 'length'

    def clearFormatting(self, label=None):
        if label is None:
            # if isinstance(lbl, AIChatUnit) or isinstance(lbl, UserChatUnit) should be added
            # Or else AttributeError: 'QWidget' object has no attribute 'getLbl' will be raised when calling getLbl()
            labels = [lbl.getLbl() for lbl in self.__getEveryLabels() if isinstance(lbl, AIChatUnit) or isinstance(lbl, UserChatUnit)]
            for lbl in labels:
                self.clearFormatting(lbl)
            return
        cursor = label.textCursor()
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        cursor.setCharFormat(format)

    def highlightText(self, label, pattern, case_sensitive):
        self.clearFormatting(label)  # Clear any previous formatting

        if pattern == '':
            return

        cursor = label.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor(DEFAULT_FOUND_TEXT_BG_COLOR))
        format.setForeground(QColor(DEFAULT_FOUND_TEXT_COLOR))

        # Ensure we start from the beginning
        cursor.setPosition(0)

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
        label_info = [{'class':label.getLbl(), 'text':label.getText(), 'pos':label.y()} for label in labels]
        selections = []

        for _ in label_info:
            pattern = text
            _['pattern'] = pattern
            if is_regex:
                if is_valid_regex(pattern):
                    if case_sensitive:
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            selections.append(_)
                    else:
                        result = re.search(pattern, _['text'])
                        if result:
                            selections.append(_)
                else:
                    if _['text'].find(text) != -1:
                        selections.append(_)
            else:
                if case_sensitive:
                    if word_only:
                        pattern = r'\b' + re.escape(text) + r'\b'
                        result = re.search(pattern, _['text'])
                        if result:
                            selections.append(_)
                    else:
                        if _['text'].find(text) != -1:
                            selections.append(_)
                else:
                    if word_only:
                        pattern = r'\b' + re.escape(text) + r'\b'
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            selections.append(_)
                    else:
                        pattern = re.escape(text)
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            selections.append(_)

        return selections

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
            self.__setResponseInfo(unit, arg)

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
            self.__setResponseInfo(unit, arg)

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