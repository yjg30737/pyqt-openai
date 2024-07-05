import base64
import os

from qtpy.QtCore import QThread, Signal, QSettings
from qtpy.QtWidgets import QMessageBox, QScrollArea, QWidget, QCheckBox, QSpinBox, QGroupBox, QVBoxLayout, QPushButton, \
    QComboBox, \
    QPlainTextEdit, \
    QFormLayout, QLabel, QFrame, QRadioButton

from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.toast import Toast


class Thread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    def __init__(self, openai_arg, number_of_images, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__openai_arg = openai_arg
        self.__number_of_images = number_of_images
        self.__stop = False

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            for _ in range(self.__number_of_images):
                if self.__stop:
                    break

                response = OPENAI_STRUCT.images.generate(
                    **self.__openai_arg
                )
                container = ImagePromptContainer(**self.__openai_arg)
                for _ in response.data:
                    image_data = base64.b64decode(_.b64_json)
                    container.data = image_data
                    container.revised_prompt = _.revised_prompt
                    container.width = self.__openai_arg['size'].split('x')[0]
                    container.height = self.__openai_arg['size'].split('x')[1]
                    self.replyGenerated.emit(container)
            self.allReplyGenerated.emit()
        except Exception as e:
            self.errorGenerated.emit(str(e))


class DallEControlWidget(QScrollArea):
    submitDallE = Signal(ImagePromptContainer)
    submitDallEAllComplete = Signal()

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        default_directory = 'image_result'

        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)
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
        if not self.__settings_ini.contains('continue_generation'):
            self.__settings_ini.setValue('continue_generation', False)
        if not self.__settings_ini.contains('number_of_images_to_create'):
            self.__settings_ini.setValue('number_of_images_to_create', 2)
        if not self.__settings_ini.contains('style'):
            self.__settings_ini.setValue('style', 'vivid')
        if not self.__settings_ini.contains('response_format'):
            self.__settings_ini.setValue('response_format', 'b64_json')
        if not self.__settings_ini.contains('save_prompt_as_text'):
            self.__settings_ini.setValue('save_prompt_as_text', True)
        if not self.__settings_ini.contains('show_prompt_on_image'):
            self.__settings_ini.setValue('show_prompt_on_image', False)
        if not self.__settings_ini.contains('prompt_type'):
            self.__settings_ini.setValue('prompt_type', 1)
        if not self.__settings_ini.contains('width'):
            self.__settings_ini.setValue('width', 1024)
        if not self.__settings_ini.contains('height'):
            self.__settings_ini.setValue('height', 1024)
        if not self.__settings_ini.contains('prompt'):
            self.__settings_ini.setValue('prompt', "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k")

        self.__quality = self.__settings_ini.value('quality', type=str)
        self.__n = self.__settings_ini.value('n', type=int)
        self.__size = self.__settings_ini.value('size', type=str)
        self.__directory = self.__settings_ini.value('directory', type=str)
        self.__is_save = self.__settings_ini.value('is_save', type=bool)
        self.__continue_generation = self.__settings_ini.value('continue_generation', type=bool)
        self.__number_of_images_to_create = self.__settings_ini.value('number_of_images_to_create', type=int)
        self.__style = self.__settings_ini.value('style', type=str)
        self.__response_format = self.__settings_ini.value('response_format', type=str)
        self.__save_prompt_as_text = self.__settings_ini.value('save_prompt_as_text', type=bool)
        self.__show_prompt_on_image = self.__settings_ini.value('show_prompt_on_image', type=bool)
        self.__prompt_type = self.__settings_ini.value('prompt_type', type=int)
        self.__width = self.__settings_ini.value('width', type=int)
        self.__height = self.__settings_ini.value('height', type=int)
        self.__prompt = self.__settings_ini.value('prompt', type=str)

        self.__settings_ini.endGroup()

    def __initUi(self):
        self.__numberOfImagesToCreateSpinBox = QSpinBox()
        self.__promptTypeToShowRadioGrpBox = QGroupBox('Prompt Type To Show')

        # generic settings
        self.__findPathWidget = FindPathWidget()
        self.__findPathWidget.setAsDirectory(True)
        self.__findPathWidget.getLineEdit().setPlaceholderText('Choose Directory to Save...')
        self.__findPathWidget.getLineEdit().setText(self.__directory)
        self.__findPathWidget.added.connect(self.__setSaveDirectory)

        self.__saveChkBox = QCheckBox('Save After Submit')
        self.__saveChkBox.setChecked(True)
        self.__saveChkBox.toggled.connect(self.__saveChkBoxToggled)
        self.__saveChkBox.setChecked(self.__is_save)

        self.__continueGenerationChkBox = QCheckBox('Continue Image Generation')
        self.__continueGenerationChkBox.setChecked(True)
        self.__continueGenerationChkBox.toggled.connect(self.__continueGenerationChkBoxToggled)
        self.__continueGenerationChkBox.setChecked(self.__continue_generation)

        self.__numberOfImagesToCreateSpinBox.setRange(2, 1000)
        self.__numberOfImagesToCreateSpinBox.setValue(self.__number_of_images_to_create)
        self.__numberOfImagesToCreateSpinBox.valueChanged.connect(self.__numberOfImagesToCreateSpinBoxValueChanged)

        self.__savePromptAsTextChkBox = QCheckBox('Save Prompt (Revised) as Text')
        self.__savePromptAsTextChkBox.setChecked(True)
        self.__savePromptAsTextChkBox.toggled.connect(self.__savePromptAsTextChkBoxToggled)
        self.__savePromptAsTextChkBox.setChecked(self.__save_prompt_as_text)

        self.__showPromptOnImageChkBox = QCheckBox('Show Prompt on Image (Working)')
        self.__showPromptOnImageChkBox.setChecked(True)
        self.__showPromptOnImageChkBox.toggled.connect(self.__showPromptOnImageChkBoxToggled)
        self.__showPromptOnImageChkBox.setChecked(self.__show_prompt_on_image)

        self.__normalOne = QRadioButton('Normal')
        self.__revisedOne = QRadioButton('Revised')

        if self.__prompt_type == 1:
            self.__normalOne.setChecked(True)
        else:
            self.__revisedOne.setChecked(True)

        self.__normalOne.toggled.connect(self.__promptTypeToggled)
        self.__revisedOne.toggled.connect(self.__promptTypeToggled)

        lay = QVBoxLayout()
        lay.addWidget(self.__normalOne)
        lay.addWidget(self.__revisedOne)
        self.__promptTypeToShowRadioGrpBox.setLayout(lay)

        self.__generalGrpBox = QGroupBox()
        self.__generalGrpBox.setTitle('General')

        lay = QVBoxLayout()
        lay.addWidget(self.__findPathWidget)
        lay.addWidget(self.__saveChkBox)
        lay.addWidget(self.__continueGenerationChkBox)
        lay.addWidget(self.__numberOfImagesToCreateSpinBox)
        lay.addWidget(self.__savePromptAsTextChkBox)
        lay.addWidget(self.__showPromptOnImageChkBox)
        lay.addWidget(self.__promptTypeToShowRadioGrpBox)
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

        self.__sizeLimitLabel = QLabel('※ Images can have a size of 1024x1024, 1024x1792 or 1792x1024 pixels.')
        self.__sizeLimitLabel.setWordWrap(True)

        self.__widthCmbBox = QComboBox()
        self.__widthCmbBox.addItems(['1024', '1792'])
        self.__widthCmbBox.setCurrentText(str(self.__width))
        self.__widthCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__heightCmbBox = QComboBox()
        self.__heightCmbBox.addItems(['1024', '1792'])
        self.__heightCmbBox.setCurrentText(str(self.__height))
        self.__heightCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__promptWidget = QPlainTextEdit()
        self.__promptWidget.setPlaceholderText('Enter prompt here...')
        self.__promptWidget.setPlainText(self.__prompt)
        self.__promptWidget.textChanged.connect(self.__dalleTextChanged)

        self.__styleCmbBox = QComboBox()
        self.__styleCmbBox.addItems(['vivid', 'natural'])
        self.__styleCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__submitBtn = QPushButton(LangClass.TRANSLATIONS['Submit'])
        self.__submitBtn.clicked.connect(self.__submit)

        self.__stopGeneratingImageBtn = QPushButton('Stop Generating Image')
        self.__stopGeneratingImageBtn.clicked.connect(self.__stopGeneratingImage)
        self.__stopGeneratingImageBtn.setEnabled(False)

        paramGrpBox = QGroupBox()
        paramGrpBox.setTitle('Parameters')

        lay = QFormLayout()
        lay.addRow('Quality', self.__qualityCmbBox)
        lay.addRow(LangClass.TRANSLATIONS['Total'], self.__nSpinBox)
        lay.addRow(self.__sizeLimitLabel)
        lay.addRow('Width', self.__widthCmbBox)
        lay.addRow('Height', self.__heightCmbBox)
        lay.addRow('Style', self.__styleCmbBox)
        lay.addRow(QLabel(LangClass.TRANSLATIONS['Prompt']))
        lay.addRow(self.__promptWidget)

        paramGrpBox.setLayout(lay)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        lay = QVBoxLayout()
        lay.addWidget(self.__generalGrpBox)
        lay.addWidget(paramGrpBox)
        lay.addWidget(sep)
        lay.addWidget(self.__submitBtn)
        lay.addWidget(self.__stopGeneratingImageBtn)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def __dalleChanged(self, v):
        sender = self.sender()
        self.__settings_ini.beginGroup('DALLE')
        if sender == self.__qualityCmbBox:
            self.__quality = v
            self.__settings_ini.setValue('quality', self.__quality)
        elif sender == self.__nSpinBox:
            self.__n = v
            self.__settings_ini.setValue('n', self.__n)
        elif sender == self.__widthCmbBox:
            if self.__widthCmbBox.currentText() == '1792' and self.__heightCmbBox.currentText() == '1792':
                self.__heightCmbBox.setCurrentText('1024')
            self.__width = v
            self.__settings_ini.setValue('width', self.__width)
        elif sender == self.__heightCmbBox:
            if self.__widthCmbBox.currentText() == '1792' and self.__heightCmbBox.currentText() == '1792':
                self.__widthCmbBox.setCurrentText('1024')
            self.__height = v
            self.__settings_ini.setValue('height', self.__height)
        elif sender == self.__styleCmbBox:
            self.__style = v
            self.__settings_ini.setValue('style', self.__style)
        self.__settings_ini.endGroup()

    def __dalleTextChanged(self):
        sender = self.sender()
        self.__settings_ini.beginGroup('DALLE')
        if isinstance(sender, QPlainTextEdit):
            if sender == self.__promptWidget:
                self.__prompt = sender.toPlainText()
                self.__settings_ini.setValue('prompt', self.__prompt)
        self.__settings_ini.endGroup()

    def __setSaveDirectory(self, directory):
        self.__directory = directory
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('directory', self.__directory)
        self.__settings_ini.endGroup()

    def __saveChkBoxToggled(self, f):
        self.__is_save = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('is_save', self.__is_save)
        self.__settings_ini.endGroup()

    def __continueGenerationChkBoxToggled(self, f):
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

    def __savePromptAsTextChkBoxToggled(self, f):
        self.__save_prompt_as_text = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('save_prompt_as_text', self.__save_prompt_as_text)
        self.__settings_ini.endGroup()
        
    def __showPromptOnImageChkBoxToggled(self, f):
        self.__show_prompt_on_image = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('show_prompt_on_image', self.__show_prompt_on_image)
        self.__settings_ini.endGroup()
        self.__promptTypeToShowRadioGrpBox.setEnabled(self.__show_prompt_on_image)

    def __promptTypeToggled(self, f):
        sender = self.sender()
        self.__settings_ini.beginGroup('DALLE')
        # Prompt type to show on the image
        # 1 is normal, 2 is revised
        if sender == self.__normalOne:
            self.__prompt_type = 1
            self.__settings_ini.setValue('prompt_type', self.__prompt_type)
        elif sender == self.__revisedOne:
            self.__prompt_type = 2
            self.__settings_ini.setValue('prompt_type', self.__prompt_type)
        self.__settings_ini.endGroup()

    def __submit(self):
        openai_arg = {
            "model": "dall-e-3",
            "prompt": self.__promptWidget.toPlainText(),
            "n": self.__n,
            "size": f'{self.__width}x{self.__height}',
            'quality': self.__quality,
            "style": self.__style,
            'response_format': self.__response_format,
        }
        number_of_images = self.__number_of_images_to_create if self.__continue_generation else 1

        self.__t = Thread(openai_arg, number_of_images)
        self.__t.start()
        self.__t.started.connect(self.__toggleWidget)
        self.__t.replyGenerated.connect(self.__afterGenerated)
        self.__t.errorGenerated.connect(self.__failToGenerate)
        self.__t.finished.connect(self.__toggleWidget)
        self.__t.allReplyGenerated.connect(self.submitDallEAllComplete)

    def __toggleWidget(self):
        f = not self.__t.isRunning()
        self.__generalGrpBox.setEnabled(f)
        self.__qualityCmbBox.setEnabled(f)
        self.__nSpinBox.setEnabled(f)
        self.__widthCmbBox.setEnabled(f)
        self.__heightCmbBox.setEnabled(f)
        self.__submitBtn.setEnabled(f)
        self.__styleCmbBox.setEnabled(f)
        if self.__continue_generation:
            self.__stopGeneratingImageBtn.setEnabled(not f)

    def __stopGeneratingImage(self):
        if self.__t.isRunning():
            self.__t.stop()

    def __failToGenerate(self, e):
        if self.isVisible():
            toast = Toast(text=e, duration=3, parent=self)
            toast.show()
        else:
            informative_text = 'Error 😥'
            detailed_text = e
            self.__notifierWidget = NotifierWidget(informative_text=informative_text, detailed_text = detailed_text)
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.window().show)
            QMessageBox.critical(self, informative_text, detailed_text)

    def __afterGenerated(self, arg):
        self.submitDallE.emit(arg)

    def getArgument(self):
        return {
            'prompt': self.__promptWidget.toPlainText(),
            'n': self.__n,
            'size': self.__size,
            'quality': self.__quality,
            'style': self.__style
        }

    def getSavePromptAsText(self):
        return self.__save_prompt_as_text

    def isSavedEnabled(self):
        return self.__is_save

    def getDirectory(self):
        return self.__directory

