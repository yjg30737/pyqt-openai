from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from pyqt_openai.test.mainWindow.image_gen_widget.imageDallEPage import ImageDallEPage
from pyqt_openai.test.mainWindow.image_gen_widget.imageStableDiffusionPage import ImageStableDiffusionPage


class LeftSideBar(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        w1 = ImageDallEPage()
        w2 = ImageStableDiffusionPage()
        tabWidget = QTabWidget()
        tabWidget.addTab(w1, 'DALL-E')
        tabWidget.addTab(w2, 'Stable Diffusion')
        lay = QVBoxLayout()
        lay.addWidget(tabWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)