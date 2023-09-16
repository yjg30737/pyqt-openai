from qtpy.QtGui import QFont
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedWidget
from qtpy.QtCore import Qt

from pyqt_openai.chat_widget.chatBrowser import ChatBrowser
from pyqt_openai.chat_widget.menuWidget import MenuWidget
from pyqt_openai.res.language_dict import LangClass


class ChatWidget(QWidget):
    def __init__(self, finish_reason=True):
        super(ChatWidget, self).__init__()
        self.__initVal(finish_reason)
        self.__initUi()

    def __initVal(self, finish_reason):
        self.__cur_id = 0
        self.__show_finished_reason_f = finish_reason

    def __initUi(self):
        self.__homeWidget = QLabel(LangClass.TRANSLATIONS['Home'])
        self.__homeWidget.setAlignment(Qt.AlignCenter)
        self.__homeWidget.setFont(QFont('Arial', 32))

        self.__chatBrowser = ChatBrowser(self.__show_finished_reason_f)

        menuWidget = MenuWidget(self.__chatBrowser)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__chatBrowser)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        chatWidget = QWidget()
        chatWidget.setLayout(lay)

        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(self.__homeWidget)
        self.__mainWidget.addWidget(chatWidget)

        self.__chatBrowser.onReplacedCurrentPage.connect(self.__mainWidget.setCurrentIndex)

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self.__mainWidget)
        lay.setAlignment(Qt.AlignTop)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def __resetWidget(self):
        self.__mainWidget.setCurrentIndex(0)

    def isNew(self):
        return self.__mainWidget.currentIndex() == 0

    def getChatBrowser(self):
        return self.__chatBrowser