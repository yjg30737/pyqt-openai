# Currently this page is home page of the application.
from __future__ import annotations

from qtpy.QtCore import Qt
from qtpy.QtGui import QFont, QPixmap
from qtpy.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from pyqt_openai import (
    DEFAULT_APP_NAME,
    LARGE_LABEL_PARAM,
    MEDIUM_LABEL_PARAM,
    QUICKSTART_MANUAL_URL,
)
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.linkLabel import LinkLabel


class ChatHome(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel(f"Welcome to {DEFAULT_APP_NAME}!", self)
        title.setFont(QFont(*LARGE_LABEL_PARAM))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(
            LangClass.TRANSLATIONS["Enjoy convenient chatting, all day long!"],
        )

        self.__quickStartManualLbl = LinkLabel()
        self.__quickStartManualLbl.setText(LangClass.TRANSLATIONS["Quick Start Manual"])
        self.__quickStartManualLbl.setUrl(QUICKSTART_MANUAL_URL)
        self.__quickStartManualLbl.setFont(QFont(*MEDIUM_LABEL_PARAM))
        self.__quickStartManualLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__background_image = QLabel()

        description.setFont(QFont(*MEDIUM_LABEL_PARAM))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        lay.addWidget(self.__quickStartManualLbl)
        lay.addWidget(self.__background_image)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def setPixmap(self, filename):
        self.__background_image.setPixmap(QPixmap(filename))
