from qtpy.QtWidgets import QWidget, QFormLayout, QSpinBox, QComboBox, QLabel, QTextEdit


class ImageStableDiffusionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        nSpinBox = QSpinBox()
        nSpinBox.setRange(1, 10)
        # nSpinBox.setValue(self.__info_dict['n'])
        # nSpinBox.valueChanged.connect(self.__nChanged)
        sizeCmbBox = QComboBox()
        sizeCmbBox.addItems(['256x256', '512x512', '1024x1024'])

        promptWidget = QTextEdit()

        lay = QFormLayout()
        lay.addRow('Total', nSpinBox)
        lay.addRow('Size', sizeCmbBox)

        lay.addRow(QLabel('Prompt'))
        lay.addRow(promptWidget)

        self.setLayout(lay)