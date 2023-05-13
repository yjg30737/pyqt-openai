from qtpy.QtWidgets import QWidget, QPushButton, QFormLayout, QSpinBox, QComboBox, QLabel, QPlainTextEdit
from qtpy.QtCore import Signal


class ImageStableDiffusionPage(QWidget):
    submit = Signal(str)

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

        self.__promptWidget = QPlainTextEdit()
        submitBtn = QPushButton('Submit')
        submitBtn.clicked.connect(self.__submit)

        lay = QFormLayout()
        lay.addRow('Total', nSpinBox)
        lay.addRow('Size', sizeCmbBox)
        lay.addRow(QLabel('Prompt'))
        lay.addRow(self.__promptWidget)
        lay.addRow(submitBtn)

        self.setLayout(lay)

    def __submit(self):
        prompt_text = self.__promptWidget.toPlainText()
        self.submit.emit(prompt_text)