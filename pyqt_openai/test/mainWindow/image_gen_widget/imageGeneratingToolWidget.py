import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget
from PyQt5.QtWidgets import QSplitter

from pyqt_openai.test.mainWindow.image_gen_widget.currentImageView import CurrentImageView
from pyqt_openai.test.mainWindow.image_gen_widget.explorerWidget import ExplorerWidget
from pyqt_openai.test.mainWindow.image_gen_widget.leftSideBar import LeftSideBar
from pyqt_openai.test.mainWindow.image_gen_widget.thumbnailView import ThumbnailView


class ImageGeneratingToolWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        leftSideBar = LeftSideBar()

        currentImageView = ThumbnailView()
        currentImageView.setFilename('Billy Eillish.png')
        explorerWidget = ExplorerWidget()

        rightWidget = QSplitter()
        rightWidget.setOrientation(Qt.Vertical)
        rightWidget.addWidget(currentImageView)
        rightWidget.addWidget(explorerWidget)
        rightWidget.setSizes([700, 300])
        rightWidget.setChildrenCollapsible(False)
        rightWidget.setHandleWidth(2)
        rightWidget.setStyleSheet(
        '''
        QSplitter::handle:vertical
        {
            background: #CCC;
            height: 1px;
        }
        ''')

        mainWidget = QSplitter()
        mainWidget.addWidget(leftSideBar)
        mainWidget.addWidget(rightWidget)
        mainWidget.setSizes([200, 800])
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setHandleWidth(2)
        mainWidget.setStyleSheet(
        '''
        QSplitter::handle:horizontal
        {
            background: #CCC;
            height: 1px;
        }
        ''')

        lay = QGridLayout()
        lay.addWidget(mainWidget)
        self.setLayout(lay)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ImageGeneratingToolWidget()
    w.show()
    sys.exit(app.exec_())
