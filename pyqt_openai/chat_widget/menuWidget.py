from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel

from pyqt_openai.chat_widget.findTextWidget import FindTextWidget
from pyqt_openai.chat_widget.chatBrowser import ChatBrowser


class MenuWidget(QWidget):
    def __init__(self, widget: ChatBrowser):
        super().__init__()
        self.__initUi(widget=widget)

    def __initUi(self, widget):
        self.__titleLbl = QLabel('Title')
        findTextWidget = FindTextWidget(widget)

        lay = QVBoxLayout()
        lay.addWidget(self.__titleLbl)
        lay.addWidget(findTextWidget)
        lay.setContentsMargins(4, 4, 4, 4)

        self.setLayout(lay)

    def setTitle(self, title):
        self.__titleLbl.setText(title)