from PyQt5.QtWidgets import QGridLayout, QWidget, QScrollArea, \
    QSizePolicy

from pyqt_openai.test.mainWindow.image_gen_widget.thumbnailView import ThumbnailView


class ExplorerWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        lay = QGridLayout()

        for row in range(24):
            for col in range(6):
                thumbnail = ThumbnailView()
                thumbnail.setFilename('Billy Eillish.png')
                thumbnail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # This line added
                lay.addWidget(thumbnail, row, col)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)