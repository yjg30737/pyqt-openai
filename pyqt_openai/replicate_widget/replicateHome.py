from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea

from pyqt_openai import CONTEXT_DELIMITER, HOW_TO_REPLICATE, LARGE_LABEL_PARAM, MEDIUM_LABEL_PARAM
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.linkLabel import LinkLabel


class ReplicateHome(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel('Welcome to Replicate Page !', self)
        title.setFont(QFont(*LARGE_LABEL_PARAM))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(LangClass.TRANSLATIONS['Generate images with Replicate API.'] + '\n'
                               + LangClass.TRANSLATIONS['You can use a lot of models to generate images, only you need to have an API key.'] + CONTEXT_DELIMITER)

        description.setFont(QFont(*MEDIUM_LABEL_PARAM))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__manualLabel = LinkLabel()
        self.__manualLabel.setText('What is the Replicate & How to use it?')
        self.__manualLabel.setUrl(HOW_TO_REPLICATE)
        self.__manualLabel.setFont(QFont(*MEDIUM_LABEL_PARAM))
        self.__manualLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        lay.addWidget(self.__manualLabel)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)