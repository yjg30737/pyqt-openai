from qtpy.QtGui import QPalette, QColor
from qtpy.QtWidgets import QTextBrowser

from pyqt_openai import MESSAGE_ADDITIONAL_HEIGHT, MESSAGE_MAXIMUM_HEIGHT, MESSAGE_PADDING


class MessageTextBrowser(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        # Transparent background
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(0, 0, 0, 0))
        self.setPalette(palette)

        # Remove edge
        self.setFrameShape(QTextBrowser.NoFrame)

        # Padding
        self.document().setDocumentMargin(MESSAGE_PADDING)

        self.setContentsMargins(0, 0, 0, 0)

    def adjustBrowserHeight(self):
        document_height = self.document().size().height() + MESSAGE_ADDITIONAL_HEIGHT
        max_height = MESSAGE_MAXIMUM_HEIGHT

        if document_height < max_height:
            self.setMinimumHeight(int(document_height))
        else:
            self.setMinimumHeight(int(max_height))
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())