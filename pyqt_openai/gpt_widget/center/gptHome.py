# Currently this page is home page of the application.

from qtpy.QtCore import Qt
from qtpy.QtGui import QFont, QPixmap
from qtpy.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea

from pyqt_openai import DEFAULT_APP_NAME, CONTEXT_DELIMITER
from pyqt_openai.widgets.linkLabel import LinkLabel


class GPTHome(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel(f'Welcome to {DEFAULT_APP_NAME}!', self)
        title.setFont(QFont('Arial', 32))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel('Enjoy convenient chatting, all day long!')

        self.__openaiApiManualLbl = LinkLabel()
        # TODO LANGUAGE
        self.__openaiApiManualLbl.setText('How to get OpenAI API Key?')
        self.__openaiApiManualLbl.setUrl('https://medium.com/@yjg30737/how-to-get-your-openai-api-key-e2193850932e')
        self.__openaiApiManualLbl.setFont(QFont('Arial', 16))
        self.__openaiApiManualLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__background_image = QLabel()

        description.setFont(QFont('Arial', 16))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        lay.addWidget(self.__background_image)
        lay.addWidget(self.__openaiApiManualLbl)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def setPixmap(self, filename):
        self.__background_image.setPixmap(QPixmap(filename))
