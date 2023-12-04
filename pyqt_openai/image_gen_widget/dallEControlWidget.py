import os

from qtpy.QtCore import QThread
from qtpy.QtCore import Signal, QSettings
from qtpy.QtWidgets import QFrame, QWidget, QCheckBox, QSpinBox, QGroupBox, QVBoxLayout, QPushButton, QComboBox, QPlainTextEdit, QFormLayout, QLabel

from pyqt_openai.customizeDialog import FindPathWidget
from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.toast import Toast


class DallEThread(QThread):
    replyGenerated = Signal(str)
    errorGenerated = Signal(str)

    def __init__(self, openai_arg, number_of_images, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__openai_arg = openai_arg
        self.__number_of_images = number_of_images

    def run(self):
        try:
            for _ in range(self.__number_of_images):
                response = OPENAI_STRUCT.images.generate(
                    **self.__openai_arg
                )

                for image_data in response.data:
                    image_url = image_data.url
                    self.replyGenerated.emit(image_url)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class DallEControlWidget(QWidget):
    submitDallE = Signal(str)
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        default_directory = 'image_result'

        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)
        self.__settings_ini.beginGroup('DALLE')

        if not self.__settings_ini.contains('quality'):
            self.__settings_ini.setValue('quality', 'standard')
        if not self.__settings_ini.contains('n'):
            self.__settings_ini.setValue('n', 1)
        if not self.__settings_ini.contains('size'):
            self.__settings_ini.setValue('size', '1024x1024')
        if not self.__settings_ini.contains('directory'):
            self.__settings_ini.setValue('directory', os.path.join(os.path.expanduser('~'), default_directory))
        if not self.__settings_ini.contains('is_save'):
            self.__settings_ini.setValue('is_save', True)
        if not self.__settings_ini.contains('continue_genearation'):
            self.__settings_ini.setValue('continue_genearation', False)
        if not self.__settings_ini.contains('number_of_images_to_create'):
            self.__settings_ini.setValue('number_of_images_to_create', 2)

        self.__quality = self.__settings_ini.value('quality', type=str)
        self.__n = self.__settings_ini.value('n', type=int)
        self.__size = self.__settings_ini.value('size', type=str)
        self.__directory = self.__settings_ini.value('directory', type=str)
        self.__is_save = self.__settings_ini.value('is_save', type=bool)
        self.__continue_generation = self.__settings_ini.value('continue_genearation', type=bool)
        self.__number_of_images_to_create = self.__settings_ini.value('number_of_images_to_create', type=int)

        self.__settings_ini.endGroup()

    def __initUi(self):
        # generic settings
        self.__findPathWidget = FindPathWidget()
        self.__findPathWidget.setAsDirectory(True)
        self.__findPathWidget.getLineEdit().setPlaceholderText('Choose Directory to Save...')
        self.__findPathWidget.getLineEdit().setText(self.__directory)
        self.__findPathWidget.added.connect(self.__setSaveDirectory)

        self.__saveChkBox = QCheckBox('Save After Submit')
        self.__saveChkBox.setChecked(self.__is_save)
        self.__saveChkBox.stateChanged.connect(self.__saveChkBoxStateChanged)

        self.__continueGenerationChkBox = QCheckBox('Continue Image Generation')
        self.__continueGenerationChkBox.setChecked(self.__continue_generation)
        self.__continueGenerationChkBox.stateChanged.connect(self.__continueGenerationChkBoxStateChanged)

        self.__numberOfImagesToCreateSpinBox = QSpinBox()
        self.__numberOfImagesToCreateSpinBox.setRange(2, 1000)
        self.__numberOfImagesToCreateSpinBox.setValue(self.__number_of_images_to_create)
        self.__numberOfImagesToCreateSpinBox.valueChanged.connect(self.__numberOfImagesToCreateSpinBoxValueChanged)

        self.__generalGrpBox = QGroupBox()
        self.__generalGrpBox.setTitle('General')

        lay = QVBoxLayout()
        lay.addWidget(self.__findPathWidget)
        lay.addWidget(self.__saveChkBox)
        lay.addWidget(self.__continueGenerationChkBox)
        lay.addWidget(self.__numberOfImagesToCreateSpinBox)
        self.__generalGrpBox.setLayout(lay)

        # parameter settings
        self.__qualityCmbBox = QComboBox()
        self.__qualityCmbBox.addItems(['standard', 'hd'])
        self.__qualityCmbBox.setCurrentText(self.__quality)
        self.__qualityCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__nSpinBox = QSpinBox()
        self.__nSpinBox.setRange(1, 10)
        self.__nSpinBox.setValue(self.__n)
        self.__nSpinBox.valueChanged.connect(self.__dalleChanged)
        self.__nSpinBox.setEnabled(False)

        self.__sizeCmbBox = QComboBox()
        self.__sizeCmbBox.addItems(['1024x1024', '1024x1792', '1792x1024'])
        self.__sizeCmbBox.setCurrentText(self.__size)
        self.__sizeCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__promptWidget = QPlainTextEdit()

        self.__submitBtn = QPushButton(LangClass.TRANSLATIONS['Submit'])
        self.__submitBtn.clicked.connect(self.__submit)

        paramGrpBox = QGroupBox()
        paramGrpBox.setTitle('Parameters')

        lay = QFormLayout()
        lay.addRow('Quality', self.__qualityCmbBox)
        lay.addRow(LangClass.TRANSLATIONS['Total'], self.__nSpinBox)
        lay.addRow(LangClass.TRANSLATIONS['Size'], self.__sizeCmbBox)
        lay.addRow(QLabel(LangClass.TRANSLATIONS['Prompt']))
        lay.addRow(self.__promptWidget)
        lay.addRow(self.__submitBtn)

        paramGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__generalGrpBox)
        lay.addWidget(paramGrpBox)

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

    def __setSaveDirectory(self, directory):
        self.__directory = directory
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('directory', self.__directory)
        self.__settings_ini.endGroup()

    def __saveChkBoxStateChanged(self, state):
        f = state == 2
        self.__is_save = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('is_save', self.__is_save)
        self.__settings_ini.endGroup()

    def __continueGenerationChkBoxStateChanged(self, state):
        f = state == 2
        self.__continue_generation = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('continue_generation', self.__continue_generation)
        self.__settings_ini.endGroup()
        self.__numberOfImagesToCreateSpinBox.setEnabled(f)

    def __numberOfImagesToCreateSpinBoxValueChanged(self, value):
        self.__number_of_images_to_create = value
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('number_of_images_to_create', self.__number_of_images_to_create)
        self.__settings_ini.endGroup()

    def __submit(self):
        openai_arg = {
            "model": "dall-e-24",
            "prompt": self.__promptWidget.toPlainText(),
            "n": self.__n,
            "size": self.__size,
            'quality': self.__quality
        }
        number_of_images = self.__number_of_images_to_create if self.__continue_generation else 1

        self.__t = DallEThread(openai_arg, number_of_images)
        self.__t.start()
        self.__t.started.connect(self.__toggleWidget)
        self.__t.replyGenerated.connect(self.__afterGenerated)
        self.__t.errorGenerated.connect(self.__failToGenerate)
        self.__t.finished.connect(self.__toggleWidget)

    def __toggleWidget(self):
        f = not self.__t.isRunning()
        self.__generalGrpBox.setEnabled(f)
        self.__qualityCmbBox.setEnabled(f)
        self.__nSpinBox.setEnabled(f)
        self.__sizeCmbBox.setEnabled(f)
        self.__submitBtn.setEnabled(f)

    def __failToGenerate(self, e):
        toast = Toast(text=e, duration=3, parent=self)
        toast.show()

    def __afterGenerated(self, image_url):
        self.submitDallE.emit(image_url)

    def getArgument(self):
        return self.__promptWidget.toPlainText(), self.__n, self.__size, self.__quality

    def isSavedEnabled(self):
        return self.__is_save

    def getDirectory(self):
        return self.__directory

