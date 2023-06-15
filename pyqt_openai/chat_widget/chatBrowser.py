from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel, \
    QStackedWidget

from pyqt_openai.chat_widget.aiChatUnit import AIChatUnit
from pyqt_openai.chat_widget.userChatUnit import UserChatUnit


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

    def showLabel(self, text, user_f, stream_f):
        self.showText(text, stream_f, user_f)
        if not stream_f:
            # change user_f type from bool to int to insert in db
            self.convUnitUpdated.emit(self.__cur_id, int(user_f), text)

    def streamFinished(self):
        self.convUnitUpdated.emit(self.__cur_id, 0, self.getLastResponse())

    def showText(self, text, stream_f, user_f):
        if self.widget().currentWidget() == self.__chatWidget:
            pass
        else:
            self.widget().setCurrentIndex(1)
        self.__setLabel(text, stream_f, user_f)

    def __setLabel(self, text, stream_f, user_f):
        chatUnit = QLabel()
        if user_f:
            chatUnit = UserChatUnit()
            chatUnit.setText(text)
        else:
            chatUnit = AIChatUnit()
            if stream_f:
                unit = self.getChatWidget().layout().itemAt(self.getChatWidget().layout().count()-1).widget()
                if isinstance(unit, AIChatUnit):
                    unit.addText(text)
                    return
            chatUnit.setText(text)

        self.getChatWidget().layout().addWidget(chatUnit)

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
                        all_text_lst.append(widget.text())

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
        self.clear()
        self.setCurId(id)
        self.widget().setCurrentIndex(1)
        for i in range(len(conv_data)):
            self.__setLabel(conv_data[i], False, not bool(i % 2))