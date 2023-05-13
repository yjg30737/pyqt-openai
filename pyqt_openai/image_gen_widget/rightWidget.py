from qtpy.QtGui import QFont
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QStackedWidget, QSplitter
from qtpy.QtCore import Qt

from pyqt_openai.image_gen_widget.explorerWidget import ExplorerWidget
from pyqt_openai.image_gen_widget.thumbnailView import ThumbnailView


class RightWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        currentImageView = ThumbnailView()
        currentImageView.setFilename('Billy Eillish.png')
        explorerWidget = ExplorerWidget()

        imageWidget = QSplitter()
        imageWidget.setOrientation(Qt.Vertical)
        imageWidget.addWidget(currentImageView)
        imageWidget.addWidget(explorerWidget)
        imageWidget.setSizes([700, 300])
        imageWidget.setChildrenCollapsible(False)
        imageWidget.setHandleWidth(2)
        imageWidget.setStyleSheet(
            '''
            QSplitter::handle:vertical
            {
                background: #CCC;
                height: 1px;
            }
            ''')

        self.__homeWidget = QLabel('Home')
        self.__homeWidget.setAlignment(Qt.AlignCenter)
        self.__homeWidget.setFont(QFont('Arial', 32))

        mainWidget = QStackedWidget()
        mainWidget.addWidget(self.__homeWidget)
        mainWidget.addWidget(imageWidget)

        lay = QGridLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)
