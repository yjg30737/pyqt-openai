from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from qtpy.QtCore import Signal

from pyqt_openai import DEFAULT_SHORTCUT_FIND_CLOSE, ICON_CLOSE
from pyqt_openai.gpt_widget.center.findTextWidget import FindTextWidget
from pyqt_openai.gpt_widget.center.chatBrowser import ChatBrowser
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.button import Button


class MenuWidget(QWidget):
    onMenuCloseClicked = Signal()

    def __init__(self, widget: ChatBrowser):
        super().__init__()
        self.__initUi(widget=widget)

    def __initUi(self, widget):
        self.__titleLbl = QLabel(LangClass.TRANSLATIONS['Title'])
        self.__findTextWidget = FindTextWidget(widget)
        self.__chatBrowser = widget

        self.__closeBtn = Button()
        self.__closeBtn.clicked.connect(self.__onMenuCloseClicked)
        self.__closeBtn.setShortcut(DEFAULT_SHORTCUT_FIND_CLOSE)
        self.__closeBtn.setStyleAndIcon(ICON_CLOSE)

        self.__closeBtn.setToolTip(LangClass.TRANSLATIONS['Close'] + f' ({DEFAULT_SHORTCUT_FIND_CLOSE})')

        lay = QVBoxLayout()
        lay.addWidget(self.__titleLbl)
        lay.addWidget(self.__findTextWidget)
        lay.addWidget(self.__closeBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(mainWidget)
        lay.addWidget(self.__closeBtn)
        lay.setContentsMargins(4, 4, 4, 4)

        self.setLayout(lay)

    def setTitle(self, title):
        self.__titleLbl.setText(title)

    def showEvent(self, event):
        self.__findTextWidget.getLineEdit().setFocus()
        self.__findTextWidget.initFind(self.__findTextWidget.getLineEdit().text())
        super().showEvent(event)

    def __onMenuCloseClicked(self):
        self.__findTextWidget.clearFormatting()
        self.onMenuCloseClicked.emit()
        self.hide()

    def getFindTextWidget(self):
        return self.__findTextWidget