from qtpy.QtGui import QFont, QPixmap
from qtpy.QtWidgets import QWidget, QScrollArea, QLabel, QVBoxLayout, QStackedWidget
from qtpy.QtCore import Qt, QSettings

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
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        if not self.__settings_ini.contains('background_image'):
            self.__settings_ini.setValue('background_image', '')

        self.__background_image = self.__settings_ini.value('background_image', type=str)

    def __initUi(self):
        self.__homeWidget = QScrollArea()
        self.__homeLbl = QLabel(LangClass.TRANSLATIONS['Home'])
        if self.__background_image:
            self.__homeLbl.setPixmap(QPixmap(self.__background_image))
        self.__homeLbl.setAlignment(Qt.AlignCenter)
        self.__homeLbl.setFont(QFont('Arial', 32))
        self.__homeWidget.setWidget(self.__homeLbl)

        self.__chatBrowser = ChatBrowser(self.__show_finished_reason_f)

        self.__menuWidget = MenuWidget(self.__chatBrowser)

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
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

    def toggleMenuWidget(self, f):
        self.__menuWidget.setVisible(f)

    def refreshCustomizedInformation(self):
        self.__background_image = self.__settings_ini.value('background_image', type=str)
        if self.__background_image:
            self.__homeLbl.setPixmap(QPixmap(self.__background_image))
