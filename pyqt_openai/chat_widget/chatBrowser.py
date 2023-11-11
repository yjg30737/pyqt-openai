import re

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel

from pyqt_openai.chat_widget.aiChatUnit import AIChatUnit
from pyqt_openai.chat_widget.userChatUnit import UserChatUnit
from pyqt_openai.util.script import is_valid_regex


class ChatBrowser(QScrollArea):
    convUnitUpdated = Signal(int, int, str, str)
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
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__chatWidget = QWidget()
        self.__chatWidget.setLayout(lay)

        self.setWidget(self.__chatWidget)
        self.setWidgetResizable(True)

    def showLabel(self, text, user_f, stream_f, finish_reason=''):
        # for question & response below the menu
        unit = self.showText(text, stream_f, user_f)
        if not stream_f:
            self.__showConvResultInfo(unit, finish_reason)
            # change user_f type from bool to int to insert in db
            self.convUnitUpdated.emit(self.__cur_id, int(user_f), text, finish_reason)

    def __getLastUnit(self) -> AIChatUnit | None:
        item = self.widget().layout().itemAt(self.widget().layout().count() - 1)
        if item:
            return item.widget()
        else:
            return None

    def __showConvResultInfo(self, unit, finish_reason):
        if isinstance(unit, AIChatUnit):
            unit.showConvResultInfo(finish_reason)

    def streamFinished(self, finish_reason):
        unit = self.__getLastUnit()
        self.__showConvResultInfo(unit, finish_reason)
        self.convUnitUpdated.emit(self.__cur_id, 0, self.getLastResponse(), finish_reason)

    def showText(self, text, stream_f, user_f):
        # if self.widget().currentWidget() == self.__chatWidget:
        #     pass
        # else:
        #     self.widget().setCurrentIndex(1)
        return self.__setLabel(text, stream_f, user_f)

    def __setLabel(self, text, stream_f, user_f):
        chatUnit = QLabel()
        if user_f:
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
                    unit.disableGUIDuringGenerateResponse()
                    unit.addText(text)
                    return
            chatUnit.setText(text)

        self.widget().layout().addWidget(chatUnit)
        return chatUnit

    def event(self, e):
        if e.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(e)

    def getAllText(self):
        all_text_lst = []
        lay = self.widget().layout()
        if lay:
            for i in range(lay.count()):
                if lay.itemAt(i) and lay.itemAt(i).widget():
                    widget = lay.itemAt(i).widget()
                    if isinstance(widget, AIChatUnit):
                        all_text_lst.append(f'Answer: {widget.text()}')
                    elif isinstance(widget, UserChatUnit):
                        all_text_lst.append(f'Question: {widget.text()}')

        return '\n'.join(all_text_lst)

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
        lay = self.widget().layout()
        if lay:
            for i in range(lay.count()-1, -1, -1):
                item = lay.itemAt(i)
                if item and item.widget():
                    lay.removeWidget(item.widget())
        self.onReplacedCurrentPage.emit(0)

    def setCurId(self, id):
        self.__cur_id = id

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
        # 1 is continue 0 is not continue
        return 1

    def setCurrentLabelIncludingTextBySliderPosition(self, text, case_sensitive=False, word_only=False, is_regex=False):
        labels = self.__getEveryLabels()
        label_info = [{'class':label, 'text':label.text(), 'pos':label.y()} for label in labels]
        res_lbl = []
        for _ in label_info:
            pattern = text
            if is_regex:
                if is_valid_regex(pattern):
                    if case_sensitive:
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            res_lbl.append(_)
                    else:
                        result = re.search(pattern, _['text'])
                        if result:
                            res_lbl.append(_)
                else:
                    if _['text'].find(text) != -1:
                        res_lbl.append(_)
            else:
                if case_sensitive:
                    if word_only:
                        pattern = r'\b' + re.escape(text) + r'\b'
                        result = re.search(pattern, _['text'])
                        if result:
                            res_lbl.append(_)
                    else:
                        if _['text'].find(text) != -1:
                            res_lbl.append(_)
                else:
                    if word_only:
                        pattern = r'\b' + re.escape(text) + r'\b'
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            res_lbl.append(_)
                    else:
                        pattern = re.escape(text)
                        result = re.search(pattern, _['text'], re.IGNORECASE)
                        if result:
                            res_lbl.append(_)

        return res_lbl

    def replaceConv(self, id, conv_data):
        """
        for showing old conversation
        """
        self.clear()
        self.setCurId(id)
        self.onReplacedCurrentPage.emit(1)
        for i in range(len(conv_data)):
            # stream is False no matter what
            unit = self.__setLabel(conv_data[i]['conv'], False, conv_data[i]['is_user'])
            self.__showConvResultInfo(unit, conv_data[i]['finish_reason'])

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