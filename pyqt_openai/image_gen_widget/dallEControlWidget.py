from qtpy.QtCore import QSettings
from qtpy.QtCore import Signal, QThread
from qtpy.QtWidgets import QWidget, QPushButton, QComboBox, QPlainTextEdit, QSpinBox, QFormLayout, QLabel

from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.toast import Toast


class DallEThread(QThread):
    replyGenerated = Signal(str)
    errorGenerated = Signal(str)

    def __init__(self, openai_arg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__openai_arg = openai_arg

    def run(self):
        try:
            response = OPENAI_STRUCT.images.generate(
                **self.__openai_arg
            )

            for image_data in response.data:
                image_url = image_data.url
                self.replyGenerated.emit(image_url)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class dallEControlWidget(QWidget):
    submitDallE = Signal(str)
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)
        self.__settings_ini.beginGroup('DALLE')
        if not self.__settings_ini.contains('quality'):
            self.__settings_ini.setValue('quality', 'standard')
        if not self.__settings_ini.contains('n'):
            self.__settings_ini.setValue('n', 1)
        if not self.__settings_ini.contains('size'):
            self.__settings_ini.setValue('size', '1024x1024')

        self.__quality = self.__settings_ini.value('quality', type=str)
        self.__n = self.__settings_ini.value('n', type=int)
        self.__size = self.__settings_ini.value('size', type=str)
        self.__settings_ini.endGroup()

    def __initUi(self):
        self.__qualityCmbBox = QComboBox()
        self.__qualityCmbBox.addItems(['standard', 'hd'])
        self.__qualityCmbBox.setCurrentText(self.__quality)
        self.__qualityCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__nSpinBox = QSpinBox()
        self.__nSpinBox.setRange(1, 10)
        self.__nSpinBox.setValue(self.__n)
        self.__nSpinBox.valueChanged.connect(self.__dalleChanged)

        self.__sizeCmbBox = QComboBox()
        self.__sizeCmbBox.addItems(['1024x1024', '1024x1792', '1792x1024'])
        self.__sizeCmbBox.setCurrentText(self.__size)
        self.__sizeCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__promptWidget = QPlainTextEdit()

        self.__submitBtn = QPushButton(LangClass.TRANSLATIONS['Submit'])
        self.__submitBtn.clicked.connect(self.__submit)

        lay = QFormLayout()
        lay.addRow('Quality', self.__qualityCmbBox)
        lay.addRow(LangClass.TRANSLATIONS['Total'], self.__nSpinBox)
        lay.addRow(LangClass.TRANSLATIONS['Size'], self.__sizeCmbBox)
        lay.addRow(QLabel(LangClass.TRANSLATIONS['Prompt']))
        lay.addRow(self.__promptWidget)
        lay.addRow(self.__submitBtn)

        self.setLayout(lay)

    def __dalleChanged(self, v):
        sender = self.sender()
        self.__settings_ini.beginGroup('DALLE')
        if sender == self.__qualityCmbBox:
            self.__quality = v
            self.__settings_ini.setValue('quality', self.__quality)
        elif sender == self.__nSpinBox:
            self.__n = v
            self.__settings_ini.setValue('n', self.__n)
        elif sender == self.__sizeCmbBox:
            self.__size = v
            self.__settings_ini.setValue('size', self.__size)
        self.__settings_ini.endGroup()

    def __submit(self):
        openai_arg = {
            "model": "dall-e-3",
            "prompt": self.__promptWidget.toPlainText(),
            "n": self.__n,
            "size": self.__size,
            'quality': self.__quality
        }
        self.__t = DallEThread(openai_arg)
        self.__submitBtn.setEnabled(False)
        self.__t.start()
        self.__t.replyGenerated.connect(self.__afterGenerated)
        self.__t.errorGenerated.connect(self.__failToGenerate)

    def __failToGenerate(self, e):
        toast = Toast(text=e, duration=3, parent=self)
        toast.show()
        self.__submitBtn.setEnabled(True)

    def __afterGenerated(self, image_url):
        self.submitDallE.emit(image_url)
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text=LangClass.TRANSLATIONS['Click this!'])
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)
        self.__submitBtn.setEnabled(True)