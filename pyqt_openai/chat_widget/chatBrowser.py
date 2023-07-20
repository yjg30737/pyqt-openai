from qtpy.QtCore import Qt, Signal, QSettings
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel, \
    QStackedWidget

from pyqt_openai.chat_widget.aiChatUnit import AIChatUnit
from pyqt_openai.chat_widget.userChatUnit import UserChatUnit
from pyqt_openai.res.language_dict import LangClass


class ChatBrowser(QScrollArea):
    convUnitUpdated = Signal(int, int, str, str)

    def __init__(self, finish_reason=True):
        super().__init__()
        self.__initVal(finish_reason)
        self.__initUi()

    def __initVal(self, finish_reason):
        self.__cur_id = 0
        self.__show_finished_reason_f = finish_reason

    def __initUi(self):
        self.__homeWidget = QLabel(LangClass.TRANSLATIONS['Home'])
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

    def showLabel(self, text, user_f, stream_f, finish_reason=''):
        # for question & response below the menu
        unit = self.showText(text, stream_f, user_f)
        if not stream_f:
            self.__setFinishReason(unit, finish_reason)
            # change user_f type from bool to int to insert in db
            self.convUnitUpdated.emit(self.__cur_id, int(user_f), text, finish_reason)

    def __getLastUnit(self) -> AIChatUnit | None:
        item = self.getChatWidget().layout().itemAt(self.getChatWidget().layout().count() - 1)
        if item:
            return item.widget()
        else:
            return None

    def __setFinishReason(self, unit, finish_reason):
        if isinstance(unit, AIChatUnit):
            unit.setFinishReason(finish_reason)

    def streamFinished(self, finish_reason):
        unit = self.__getLastUnit()
        self.__setFinishReason(unit, finish_reason)
        self.convUnitUpdated.emit(self.__cur_id, 0, self.getLastResponse(), finish_reason)

    def showText(self, text, stream_f, user_f):
        if self.widget().currentWidget() == self.__chatWidget:
            pass
        else:
            self.widget().setCurrentIndex(1)
        return self.__setLabel(text, stream_f, user_f)

    def __setLabel(self, text, stream_f, user_f):
        chatUnit = QLabel()
        if user_f:
            chatUnit = UserChatUnit()
            chatUnit.setText(text)
        else:
            chatUnit = AIChatUnit()
            if stream_f:
                unit = self.__getLastUnit()
                if isinstance(unit, AIChatUnit):
                    unit.addText(text)
                    return
            chatUnit.setText(text)
            chatUnit.showFinishReason(self.__show_finished_reason_f)

        self.getChatWidget().layout().addWidget(chatUnit)
        return chatUnit

    def event(self, e):
        if e.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(e)

    def getAllText(self):
        all_text_lst = []
        lay = self.getChatWidget().layout()
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
        lay = self.getChatWidget().layout()
        if lay:
            i = lay.count()-1
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, AIChatUnit):
                    return widget.text()
        return ''

    def getLastFinishReason(self):
        lay = self.getChatWidget().layout()
        if lay:
            i = lay.count()-1
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, AIChatUnit):
                    return widget.getFinishReason()
        return ''

    def getEveryResponse(self):
        lay = self.getChatWidget().layout()
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
        """
        for showing old conversation
        """
        self.clear()
        self.setCurId(id)
        self.widget().setCurrentIndex(1)
        for i in range(len(conv_data)):
            # stream is False no matter what
            unit = self.__setLabel(conv_data[i]['conv'], False, conv_data[i]['is_user'])
            self.__setFinishReason(unit, conv_data[i]['finish_reason'])

    def toggle_show_finished_reason_f(self, f):
        self.__show_finished_reason_f = f
        lay = self.getChatWidget().layout()
        if lay:
            for i in range(lay.count()):
                item = lay.itemAt(i)
                if item and item.widget():
                    unit = item.widget()
                    if isinstance(unit, AIChatUnit):
                        lbl = unit.findChild(QLabel, 'finishReasonLbl')
                        if isinstance(lbl, QLabel):
                            lbl.setVisible(self.__show_finished_reason_f)