from qtpy.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from qtpy.QtCore import Signal

from pyqt_openai.image_gen_widget.imageDallEPage import ImageDallEPage
from pyqt_openai.image_gen_widget.imageStableDiffusionPage import ImageStableDiffusionPage


class RightSideBar(QWidget):
    submitDallE = Signal(str)
    submitSd = Signal(bytes)
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        w1 = ImageDallEPage()
        w1.notifierWidgetActivated.connect(self.notifierWidgetActivated)
        w2 = ImageStableDiffusionPage()
        w2.notifierWidgetActivated.connect(self.notifierWidgetActivated)

        w1.submitDallE.connect(self.submitDallE)
        w2.submitSd.connect(self.submitSd)

        tabWidget = QTabWidget()
        tabWidget.addTab(w1, 'DALL-E')
        tabWidget.addTab(w2, 'Stable Diffusion')
        lay = QVBoxLayout()
        lay.addWidget(tabWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)