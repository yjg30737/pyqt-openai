from chat_widget.findTextWidget import FindTextWidget
from qtpy.QtCore import QPropertyAnimation, QAbstractAnimation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QFrame

from pyqt_openai.chat_widget.chatBrowser import ChatBrowser
from pyqt_openai.svgButton import SvgButton


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