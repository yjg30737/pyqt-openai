from qtpy.QtGui import QFont, QPixmap
from qtpy.QtWidgets import QWidget, QScrollArea, QLabel, QVBoxLayout, QStackedWidget
from qtpy.QtCore import Qt, QSettings

from pyqt_openai.chat_widget.chatBrowser import ChatBrowser
from pyqt_openai.chat_widget.menuWidget import MenuWidget
from pyqt_openai.res.language_dict import LangClass


class ChatWidget(QWidget):
    def __init__(self):
        super(ChatWidget, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)

        if not self.__settings_ini.contains('background_image'):
            self.__settings_ini.setValue('background_image', '')
        if not self.__settings_ini.contains('user_image'):
            self.__settings_ini.setValue('user_image', 'ico/user.png')
        if not self.__settings_ini.contains('ai_image'):
            self.__settings_ini.setValue('ai_image', 'ico/openai.png')

        self.__background_image = self.__settings_ini.value('background_image', type=str)
        self.__user_image = self.__settings_ini.value('user_image', type=str)
        self.__ai_image = self.__settings_ini.value('ai_image', type=str)

    def __initUi(self):
        self.__homeWidget = QScrollArea()
        self.__homeLbl = QLabel(LangClass.TRANSLATIONS['Home'])
        self.__homeLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__homeLbl.setFont(QFont('Arial', 32))

        self.__chatBrowser = ChatBrowser()

        self.__menuWidget = MenuWidget(self.__chatBrowser)

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
        lay.addWidget(self.__chatBrowser)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        chatWidget = QWidget()
        chatWidget.setLayout(lay)
        chatWidget.setMinimumWidth(600)

        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(self.__homeWidget)
        self.__mainWidget.addWidget(chatWidget)

        self.__chatBrowser.onReplacedCurrentPage.connect(self.__mainWidget.setCurrentIndex)

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.addWidget(self.__mainWidget)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

        self.refreshCustomizedInformation()
        self.__homeWidget.setWidget(self.__homeLbl)
        self.__homeWidget.setWidgetResizable(True)

    def showTitle(self, title):
        self.__menuWidget.setTitle(title)

    def isNew(self):
        return self.__mainWidget.currentIndex() == 0

    def getChatBrowser(self):
        return self.__chatBrowser

    def toggleMenuWidget(self, f):
        self.__menuWidget.setVisible(f)

    def refreshCustomizedInformation(self):
        self.__background_image = self.__settings_ini.value('background_image', type=str)
        self.__user_image = self.__settings_ini.value('user_image', type=str)
        self.__ai_image = self.__settings_ini.value('ai_image', type=str)

        if self.__background_image:
            self.__homeLbl.setPixmap(QPixmap(self.__background_image))
        if self.__user_image:
            self.__chatBrowser.setUserImage(self.__user_image)
        if self.__ai_image:
            self.__chatBrowser.setAIImage(self.__ai_image)