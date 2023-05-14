from qtpy.QtWidgets import QWidget, QPushButton, QFormLayout, QSpinBox, QComboBox, QLabel, QPlainTextEdit
from qtpy.QtCore import Signal

from pyqt_openai.notifier import NotifierWidget


class ImageStableDiffusionPage(QWidget):
    submit = Signal(str)
    notifierWidgetActivated = Signal()

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
        self.__submitBtn = QPushButton('Submit')
        self.__submitBtn.clicked.connect(self.__submit)

        lay = QFormLayout()
        lay.addRow('Total', nSpinBox)
        lay.addRow('Size', sizeCmbBox)
        lay.addRow(QLabel('Prompt'))
        lay.addRow(self.__promptWidget)
        lay.addRow(self.__submitBtn)

        self.setLayout(lay)

    def __submit(self):
        prompt_text = self.__promptWidget.toPlainText()
        self.submit.emit(prompt_text)

    def __afterGenerated(self, image_url):
        self.submit.emit(image_url)
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text='Response 👌', detailed_text='Click this!')
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)
        self.__submitBtn.setEnabled(True)
