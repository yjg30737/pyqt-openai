import sys

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QGridLayout, QWidget
from qtpy.QtWidgets import QSplitter

from pyqt_openai.image_gen_widget.explorerWidget import ExplorerWidget
from pyqt_openai.image_gen_widget.leftSideBar import LeftSideBar
from pyqt_openai.image_gen_widget.rightWidget import RightWidget
from pyqt_openai.image_gen_widget.thumbnailView import ThumbnailView


class ImageGeneratingToolWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        leftSideBar = LeftSideBar()

        rightWidget = RightWidget()

        mainWidget = QSplitter()
        mainWidget.addWidget(leftSideBar)
        mainWidget.addWidget(rightWidget)
        mainWidget.setSizes([300, 700])
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
        lay.setContentsMargins(2, 2, 2, 2)
        self.setLayout(lay)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ImageGeneratingToolWidget()
    w.show()
    sys.exit(app.exec_())
