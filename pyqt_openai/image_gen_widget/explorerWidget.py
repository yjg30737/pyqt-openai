from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGridLayout, QWidget, QScrollArea, \
    QSizePolicy
from qtpy.QtCore import Qt, Signal

from pyqt_openai.image_gen_widget.thumbnailView import ThumbnailView


class ExplorerWidget(QScrollArea):
    clicked = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def insertWidgetAsFirst(self, widget):
        lay = self.widget().layout()

        checkout = 6
        for i in range(lay.count()):
            r_idx, c_idx = divmod(i, checkout)
            item = lay.itemAtPosition(r_idx, c_idx)
            if item is not None:
                if checkout-c_idx == 1:
                    r_idx += 1
                    c_idx = -1
                lay.addWidget(item.widget(), r_idx, c_idx+1)
                lay.setColumnStretch(c_idx+1, 1)

        # Insert the new widget in the top-left corner
        lay.addWidget(widget, 0, 0)

    def addContent(self, content):
        thumbnail = ThumbnailView()
        thumbnail.setContent(content)
        thumbnail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.insertWidgetAsFirst(thumbnail)

    def addFilename(self, filename):
        thumbnail = ThumbnailView()
        thumbnail.clicked.connect(self.clicked)
        thumbnail.setFilename(filename)
        thumbnail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.insertWidgetAsFirst(thumbnail)
