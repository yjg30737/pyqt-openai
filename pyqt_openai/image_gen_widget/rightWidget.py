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

        homeWidget = QLabel('Home')
        homeWidget.setAlignment(Qt.AlignCenter)
        homeWidget.setFont(QFont('Arial', 32))

        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(homeWidget)
        self.__mainWidget.addWidget(imageWidget)

        lay = QGridLayout()
        lay.addWidget(self.__mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def showResult(self, prompt_text):
        self.__mainWidget.setCurrentIndex(1)
