from qtpy.QtWidgets import QWidget, QHBoxLayout

from pyqt_openai.chat_widget.findTextWidget import FindTextWidget
from pyqt_openai.chat_widget.chatBrowser import ChatBrowser


class MenuWidget(QWidget):
    def __init__(self, widget: ChatBrowser):
        super().__init__()
        self.__initUi(widget=widget)

    def __initUi(self, widget):
        findTextWidget = FindTextWidget(widget)

        lay = QHBoxLayout()
        lay.addWidget(findTextWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)