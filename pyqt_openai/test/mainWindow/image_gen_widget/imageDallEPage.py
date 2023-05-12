from PyQt5.QtWidgets import QWidget, QComboBox, QSpinBox, QFormLayout, QTextEdit, QLabel


class ImageDallEPage(QWidget):
    # class name: ImageDatabase
    # file name: imageDb
    def __init__(self):
        super().__init__()
        # self.__initVal()
        self.__initUi()


    def __initUi(self):
        # modelCmbBox.addItems(['DALL-E', 'Midjourney', 'Stable Diffusion'])
        nSpinBox = QSpinBox()
        nSpinBox.setRange(1, 10)
        # nSpinBox.setValue(self.__info_dict['n'])
        # nSpinBox.valueChanged.connect(self.__nChanged)
        sizeCmbBox = QComboBox()
        sizeCmbBox.addItems(['256x256', '512x512', '1024x1024'])
        # sizeCmbBox.setCurrentText(f"{self.__info_dict['width']}x{self.__info_dict['height']}")
        sizeCmbBox.currentTextChanged.connect(self.__sizeChanged)

        promptWidget = QTextEdit()

        lay = QFormLayout()
        lay.addRow('Total', nSpinBox)
        lay.addRow('Size', sizeCmbBox)
        lay.addRow(QLabel('Prompt'))
        lay.addRow(promptWidget)

        self.setLayout(lay)

    def __nChanged(self, v):
        pass
        # self.__db.updateInfo(3, 'n', v)

    def __sizeChanged(self, v):
        width, height = v.split('x')
        # self.__db.updateInfo(3, 'width', width)
        # self.__db.updateInfo(3, 'height', height)
