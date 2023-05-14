import sys

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QPushButton, QFileDialog
from qtpy.QtWidgets import QSplitter

from pyqt_openai.image_gen_widget.leftSideBar import LeftSideBar
from pyqt_openai.image_gen_widget.rightWidget import RightWidget
from pyqt_openai.svgButton import SvgButton


class ImageGeneratingToolWidget(QWidget):
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__leftSideBarWidget = LeftSideBar()
        self.__leftSideBarWidget.notifierWidgetActivated.connect(self.notifierWidgetActivated)

        self.__rightWidget = RightWidget()
        self.__leftSideBarWidget.submit.connect(self.__rightWidget.showResult)

        self.__sideBarBtn = SvgButton()
        self.__sideBarBtn.setIcon('ico/sidebar.svg')
        self.__sideBarBtn.setCheckable(True)
        self.__sideBarBtn.setToolTip('Settings')
        self.__sideBarBtn.setChecked(True)
        self.__sideBarBtn.toggled.connect(self.__leftSideBarWidget.setVisible)

        self.__historyBtn = SvgButton()
        self.__historyBtn.setIcon('ico/history.svg')
        self.__historyBtn.setCheckable(True)
        self.__historyBtn.setToolTip('History')
        self.__historyBtn.setChecked(True)
        self.__historyBtn.toggled.connect(self.__rightWidget.getExplorerWidget().setVisible)

        lay = QHBoxLayout()
        lay.addWidget(self.__sideBarBtn)
        lay.addWidget(self.__historyBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__leftSideBarWidget)
        mainWidget.addWidget(self.__rightWidget)
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

        testWidget = QPushButton()
        testWidget.clicked.connect(self.chooseImage)

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
        lay.addWidget(sep)
        lay.addWidget(mainWidget)
        lay.addWidget(testWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setLayout(lay)

    def chooseImage(self):
        filename = QFileDialog.getOpenFileName(self, 'Find', '', 'Image Files (*.png)')
        if filename[0]:
            filename = filename[0]
            self.__rightWidget.getExplorerWidget().addFilename(filename)

    def showAiToolBar(self, f):
        self.__menuWidget.setVisible(f)

    def setAIEnabled(self, f):
        self.__leftSideBarWidget.setEnabled(f)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ImageGeneratingToolWidget()
    w.show()
    sys.exit(app.exec_())
