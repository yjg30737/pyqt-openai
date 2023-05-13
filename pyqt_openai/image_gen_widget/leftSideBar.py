from qtpy.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from qtpy.QtCore import Signal

from pyqt_openai.image_gen_widget.imageDallEPage import ImageDallEPage
from pyqt_openai.image_gen_widget.imageStableDiffusionPage import ImageStableDiffusionPage


class LeftSideBar(QWidget):
    submit = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        w1 = ImageDallEPage()
        w2 = ImageStableDiffusionPage()

        w1.submit.connect(self.submit)
        w2.submit.connect(self.submit)

        tabWidget = QTabWidget()
        tabWidget.addTab(w1, 'DALL-E')
        tabWidget.addTab(w2, 'Stable Diffusion')
        lay = QVBoxLayout()
        lay.addWidget(tabWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)