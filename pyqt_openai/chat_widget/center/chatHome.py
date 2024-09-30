# Currently this page is home page of the application.

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea

from pyqt_openai import DEFAULT_APP_NAME, HOW_TO_GET_OPENAI_API_KEY_URL, LARGE_LABEL_PARAM, MEDIUM_LABEL_PARAM
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.linkLabel import LinkLabel


class ChatHome(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel(f"Welcome to {DEFAULT_APP_NAME}!", self)
        title.setFont(QFont(LARGE_LABEL_PARAM))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(LangClass.TRANSLATIONS['Enjoy convenient chatting, all day long!'])

        self.__quickStartManualLbl = LinkLabel()
        self.__quickStartManualLbl.setText(LangClass.TRANSLATIONS['Quick Start Manual'])
        self.__quickStartManualLbl.setUrl(HOW_TO_GET_OPENAI_API_KEY_URL)
        self.__quickStartManualLbl.setFont(QFont(MEDIUM_LABEL_PARAM))
        self.__quickStartManualLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__openaiApiManualLbl = LinkLabel()
        self.__openaiApiManualLbl.setText(LangClass.TRANSLATIONS['How to get OpenAI API Key?'])
        self.__openaiApiManualLbl.setUrl(HOW_TO_GET_OPENAI_API_KEY_URL)
        self.__openaiApiManualLbl.setFont(QFont(MEDIUM_LABEL_PARAM))
        self.__openaiApiManualLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__background_image = QLabel()

        description.setFont(QFont(MEDIUM_LABEL_PARAM))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        lay.addWidget(self.__quickStartManualLbl)
        lay.addWidget(self.__openaiApiManualLbl)
        lay.addWidget(self.__background_image)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def setPixmap(self, filename):
        self.__background_image.setPixmap(QPixmap(filename))
