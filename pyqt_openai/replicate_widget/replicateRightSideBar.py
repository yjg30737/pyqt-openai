import os

from qtpy.QtCore import Signal, QSettings, Qt
from qtpy.QtWidgets import QLineEdit, QScrollArea, QMessageBox, QWidget, QCheckBox, QSpinBox, QGroupBox, QVBoxLayout, \
    QPushButton, \
    QPlainTextEdit, \
    QFormLayout, QLabel, QSplitter

from pyqt_openai import INI_FILE_NAME, IMAGE_DEFAULT_SAVE_DIRECTORY
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.replicate_widget.replicateThread import ReplicateThread
from pyqt_openai.util.replicate_script import ReplicateWrapper
from pyqt_openai.util.script import getSeparator
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.toast import Toast


class ReplicateRightSideBarWidget(QScrollArea):
    submitReplicate = Signal(ImagePromptContainer)
    submitReplicateAllComplete = Signal()

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        default_directory = IMAGE_DEFAULT_SAVE_DIRECTORY

        self.__settings_ini = QSettings(INI_FILE_NAME, QSettings.Format.IniFormat)
        self.__settings_ini.beginGroup('REPLICATE')
        if not self.__settings_ini.contains('replicate_api_token'):
            self.__settings_ini.setValue('replicate_api_token', '')
        if not self.__settings_ini.contains('model'):
            self.__settings_ini.setValue('model', 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b')
        if not self.__settings_ini.contains('width'):
            self.__settings_ini.setValue('width', 768)
        if not self.__settings_ini.contains('height'):
            self.__settings_ini.setValue('height', 768)
        if not self.__settings_ini.contains('prompt'):
            self.__settings_ini.setValue('prompt', "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k")
        if not self.__settings_ini.contains('negative_prompt'):
            self.__settings_ini.setValue('negative_prompt', "ugly, deformed, noisy, blurry, distorted")
        if not self.__settings_ini.contains('directory'):
            self.__settings_ini.setValue('directory', os.path.join(os.path.expanduser('~'), default_directory))
        if not self.__settings_ini.contains('is_save'):
            self.__settings_ini.setValue('is_save', True)
        if not self.__settings_ini.contains('continue_generation'):
            self.__settings_ini.setValue('continue_generation', False)
        if not self.__settings_ini.contains('number_of_images_to_create'):
            self.__settings_ini.setValue('number_of_images_to_create', 2)
        if not self.__settings_ini.contains('save_prompt_as_text'):
            self.__settings_ini.setValue('save_prompt_as_text', True)
        if not self.__settings_ini.contains('show_prompt_on_image'):
            self.__settings_ini.setValue('show_prompt_on_image', False)

        self.__directory = self.__settings_ini.value('directory', type=str)
        self.__api_key = self.__settings_ini.value('replicate_api_token', type=str)
        self.__model = self.__settings_ini.value('model', type=str)
        self.__width = self.__settings_ini.value('width', type=int)
        self.__height = self.__settings_ini.value('height', type=int)
        self.__prompt = self.__settings_ini.value('prompt', type=str)
        self.__negative_prompt = self.__settings_ini.value('negative_prompt', type=str)
        self.__is_save = self.__settings_ini.value('is_save', type=bool)
        self.__continue_generation = self.__settings_ini.value('continue_generation', type=bool)
        self.__number_of_images_to_create = self.__settings_ini.value('number_of_images_to_create', type=int)
        self.__save_prompt_as_text = self.__settings_ini.value('save_prompt_as_text', type=bool)

        self.__wrapper = ReplicateWrapper(self.__api_key)
        self.__settings_ini.endGroup()

    def __initUi(self):
        self.__apiKeyLineEdit = QLineEdit()
        self.__apiKeyLineEdit.setPlaceholderText(LangClass.TRANSLATIONS['Enter Replicate API Key...'])
        self.__apiKeyLineEdit.setText(self.__api_key)
        self.__apiKeyLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.__apiKeyLineEdit.textChanged.connect(self.__replicateChanged)

        self.__numberOfImagesToCreateSpinBox = QSpinBox()

        self.__findPathWidget = FindPathWidget()
        self.__findPathWidget.setAsDirectory(True)
        self.__findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS['Choose Directory to Save...'])
        self.__findPathWidget.getLineEdit().setText(self.__directory)
        self.__findPathWidget.added.connect(self.__setSaveDirectory)

        self.__saveChkBox = QCheckBox(LangClass.TRANSLATIONS['Save After Submit'])
        self.__saveChkBox.setChecked(True)
        self.__saveChkBox.toggled.connect(self.__saveChkBoxToggled)
        self.__saveChkBox.setChecked(self.__is_save)

        self.__continueGenerationChkBox = QCheckBox(LangClass.TRANSLATIONS['Continue Image Generation'])
        self.__continueGenerationChkBox.setChecked(True)
        self.__continueGenerationChkBox.toggled.connect(self.__continueGenerationChkBoxToggled)
        self.__continueGenerationChkBox.setChecked(self.__continue_generation)

        self.__modelTextEdit = QPlainTextEdit()
        self.__modelTextEdit.setPlainText(self.__model)
        self.__modelTextEdit.textChanged.connect(self.__replicateTextChanged)

        self.__widthSpinBox = QSpinBox()
        self.__widthSpinBox.setRange(512, 1392)
        self.__widthSpinBox.setSingleStep(8)
        self.__widthSpinBox.setValue(self.__width)
        self.__widthSpinBox.valueChanged.connect(self.__replicateChanged)

        self.__heightSpinBox = QSpinBox()
        self.__heightSpinBox.setRange(512, 1392)
        self.__heightSpinBox.setSingleStep(8)
        self.__heightSpinBox.setValue(self.__height)
        self.__heightSpinBox.valueChanged.connect(self.__replicateChanged)

        self.__numberOfImagesToCreateSpinBox.setRange(2, 1000)
        self.__numberOfImagesToCreateSpinBox.setValue(self.__number_of_images_to_create)
        self.__numberOfImagesToCreateSpinBox.valueChanged.connect(self.__numberOfImagesToCreateSpinBoxValueChanged)

        self.__savePromptAsTextChkBox = QCheckBox(LangClass.TRANSLATIONS['Save Prompt as Text'])
        self.__savePromptAsTextChkBox.setChecked(True)
        self.__savePromptAsTextChkBox.toggled.connect(self.__savePromptAsTextChkBoxToggled)
        self.__savePromptAsTextChkBox.setChecked(self.__save_prompt_as_text)

        self.__generalGrpBox = QGroupBox()
        self.__generalGrpBox.setTitle(LangClass.TRANSLATIONS['General'])

        lay = QVBoxLayout()
        lay.addWidget(self.__apiKeyLineEdit)
        lay.addWidget(self.__findPathWidget)
        lay.addWidget(self.__saveChkBox)
        lay.addWidget(self.__continueGenerationChkBox)
        lay.addWidget(self.__numberOfImagesToCreateSpinBox)
        lay.addWidget(self.__savePromptAsTextChkBox)
        self.__generalGrpBox.setLayout(lay)

        self.__promptWidget = QPlainTextEdit()
        self.__promptWidget.setPlainText(self.__prompt)
        self.__promptWidget.textChanged.connect(self.__replicateTextChanged)

        self.__negativePromptWidget = QPlainTextEdit()
        self.__negativePromptWidget.setPlaceholderText('ugly, deformed, noisy, blurry, distorted')
        self.__negativePromptWidget.setPlainText(self.__negative_prompt)
        self.__negativePromptWidget.textChanged.connect(self.__replicateTextChanged)

        self.__submitBtn = QPushButton(LangClass.TRANSLATIONS['Submit'])
        self.__submitBtn.clicked.connect(self.__submit)

        self.__stopGeneratingImageBtn = QPushButton(LangClass.TRANSLATIONS['Stop Generating Image'])
        self.__stopGeneratingImageBtn.clicked.connect(self.__stopGeneratingImage)
        self.__stopGeneratingImageBtn.setEnabled(False)

        paramGrpBox = QGroupBox()
        paramGrpBox.setTitle(LangClass.TRANSLATIONS['Parameters'])

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Prompt']))
        lay.addWidget(self.__promptWidget)
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Negative Prompt']))
        lay.addWidget(self.__negativePromptWidget)
        promptWidget = QWidget()
        promptWidget.setLayout(lay)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS['Model'], self.__modelTextEdit)
        lay.addRow(LangClass.TRANSLATIONS['Width'], self.__widthSpinBox)
        lay.addRow(LangClass.TRANSLATIONS['Height'], self.__heightSpinBox)
        otherParamWidget = QWidget()
        otherParamWidget.setLayout(lay)

        splitter = QSplitter()
        splitter.addWidget(otherParamWidget)
        splitter.addWidget(promptWidget)
        splitter.setHandleWidth(1)
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([500, 500])
        splitter.setStyleSheet("QSplitterHandle {background-color: lightgray;}")

        lay = QVBoxLayout()
        lay.addWidget(splitter)
        paramGrpBox.setLayout(lay)

        sep = getSeparator('horizontal')

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

    def __replicateChanged(self, v):
        sender = self.sender()
        self.__settings_ini.beginGroup('REPLICATE')
        if sender == self.__apiKeyLineEdit:
            self.__api_key = v
            self.__settings_ini.setValue('replicate_api_token', self.__api_key)
        elif sender == self.__widthSpinBox:
            self.__width = v
            self.__settings_ini.setValue('width', self.__width)
        elif sender == self.__heightSpinBox:
            self.__height = v
            self.__settings_ini.setValue('height', self.__height)
        self.__settings_ini.endGroup()

    def __replicateTextChanged(self):
        sender = self.sender()
        self.__settings_ini.beginGroup('REPLICATE')
        if isinstance(sender, QPlainTextEdit):
            if sender == self.__modelTextEdit:
                self.__model = sender.toPlainText()
                self.__settings_ini.setValue('model', self.__model)
            elif sender == self.__promptWidget:
                self.__prompt = sender.toPlainText()
                self.__settings_ini.setValue('prompt', self.__prompt)
            elif sender == self.__negativePromptWidget:
                self.__negative_prompt = sender.toPlainText()
                self.__settings_ini.setValue('negative_prompt', self.__negative_prompt)
        self.__settings_ini.endGroup()

    def __setSaveDirectory(self, directory):
        self.__directory = directory
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('directory', self.__directory)
        self.__settings_ini.endGroup()

    def __saveChkBoxToggled(self, f):
        self.__is_save = f
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('is_save', self.__is_save)
        self.__settings_ini.endGroup()

    def __continueGenerationChkBoxToggled(self, f):
        self.__continue_generation = f
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('continue_generation', self.__continue_generation)
        self.__settings_ini.endGroup()
        self.__numberOfImagesToCreateSpinBox.setEnabled(f)

    def __numberOfImagesToCreateSpinBoxValueChanged(self, value):
        self.__number_of_images_to_create = value
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('number_of_images_to_create', self.__number_of_images_to_create)
        self.__settings_ini.endGroup()

    def __savePromptAsTextChkBoxToggled(self, f):
        self.__save_prompt_as_text = f
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('save_prompt_as_text', self.__save_prompt_as_text)
        self.__settings_ini.endGroup()

    def __submit(self):
        arg = {
            "model": self.__model,
            "prompt": self.__promptWidget.toPlainText(),
            "negative_prompt": self.__negativePromptWidget.toPlainText(),
            "width": self.__width,
            "height": self.__height,
        }
        number_of_images = self.__number_of_images_to_create if self.__continue_generation else 1

        self.__api_key = self.__apiKeyLineEdit.text().strip()
        self.__wrapper.set_api(self.__api_key)

        self.__t = ReplicateThread(self.__wrapper, self.__model, arg, number_of_images)
        self.__t.start()
        self.__t.started.connect(self.__toggleWidget)
        self.__t.replyGenerated.connect(self.__afterGenerated)
        self.__t.errorGenerated.connect(self.__failToGenerate)
        self.__t.finished.connect(self.__toggleWidget)
        self.__t.allReplyGenerated.connect(self.submitReplicateAllComplete)

    def __toggleWidget(self):
        f = not self.__t.isRunning()
        self.__generalGrpBox.setEnabled(f)
        self.__widthSpinBox.setEnabled(f)
        self.__heightSpinBox.setEnabled(f)
        self.__submitBtn.setEnabled(f)
        if self.__continue_generation:
            self.__stopGeneratingImageBtn.setEnabled(not f)

    def __stopGeneratingImage(self):
        if self.__t.isRunning():
            self.__t.stop()

    def __failToGenerate(self, event):
        if self.isVisible():
            toast = Toast(text=event, parent=self)
            toast.show()
        else:
            informative_text = 'Error 😥'
            detailed_text = event
            self.__notifierWidget = NotifierWidget(informative_text=informative_text, detailed_text = detailed_text)
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.window().show)
            QMessageBox.critical(self, informative_text, detailed_text)

    def __afterGenerated(self, result):
        self.submitReplicate.emit(result)

    def getArgument(self):
        return {
            'prompt': self.__promptWidget.toPlainText(),
            'negative_prompt': self.__negativePromptWidget.toPlainText(),
            'width': self.__width,
            'height': self.__height,
        }

    def getSavePromptAsText(self):
        return self.__save_prompt_as_text

    def isSavedEnabled(self):
        return self.__is_save

    def getDirectory(self):
        return self.__directory
