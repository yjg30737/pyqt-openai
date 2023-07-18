import openai

from qtpy.QtWidgets import QWidget, QPushButton, QComboBox, QPlainTextEdit, QSpinBox, QFormLayout, QTextEdit, QLabel
from qtpy.QtCore import Signal, QThread

from pyqt_openai.notifier import NotifierWidget
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
            response = openai.Image.create(
                **self.__openai_arg
            )

            for image_data in response['data']:
                image_url = image_data['url']
                self.replyGenerated.emit(image_url)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class ImageDallEPage(QWidget):
    submitDallE = Signal(str)
    notifierWidgetActivated = Signal()
    # class name: ImageDatabase
    # file name: imageDb

    def __init__(self):
        super().__init__()
        # self.__initVal()
        self.__initUi()

    def __initUi(self):
        self.__nSpinBox = QSpinBox()
        self.__nSpinBox.setRange(1, 10)
        # self.__nSpinBox.setValue(self.__info_dict['n'])
        # self.__nSpinBox.valueChanged.connect(self.__nChanged)
        self.__sizeCmbBox = QComboBox()
        self.__sizeCmbBox.addItems(['256x256', '512x512', '1024x1024'])
        # self.__sizeCmbBox.setCurrentText(f"{self.__info_dict['width']}x{self.__info_dict['height']}")
        self.__sizeCmbBox.currentTextChanged.connect(self.__sizeChanged)

        self.__promptWidget = QPlainTextEdit()
        self.__submitBtn = QPushButton(LangClass.TRANSLATIONS['Submit'])
        self.__submitBtn.clicked.connect(self.__submit)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS['Total'], self.__nSpinBox)
        lay.addRow(LangClass.TRANSLATIONS['Size'], self.__sizeCmbBox)
        lay.addRow(QLabel(LangClass.TRANSLATIONS['Prompt']))
        lay.addRow(self.__promptWidget)
        lay.addRow(self.__submitBtn)

        self.setLayout(lay)

    def __nChanged(self, v):
        pass
        # self.__db.updateInfo(3, 'n', v)

    def __sizeChanged(self, v):
        width, height = v.split('x')
        # self.__db.updateInfo(3, 'width', width)
        # self.__db.updateInfo(3, 'height', height)

    def __submit(self):
        # openai_arg = {
        #     "prompt": self.__prompt.getContent(),
        #     "n": info_dict['n'],
        #     "size": f"{info_dict['width']}x{info_dict['height']}"
        # }
        openai_arg = {
            "prompt": self.__promptWidget.toPlainText(),
            "n": self.__nSpinBox.value(),
            "size": self.__sizeCmbBox.currentText()
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
