from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLineEdit, QScrollArea, QMessageBox, QWidget, QCheckBox, QSpinBox, QGroupBox, QVBoxLayout, \
    QPushButton, \
    QPlainTextEdit, \
    QFormLayout, QLabel, QSplitter

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.replicate_widget.replicateThread import ReplicateThread
from pyqt_openai.util.replicate_script import ReplicateWrapper
from pyqt_openai.util.script import getSeparator
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.notifier import NotifierWidget


class ReplicateRightSideBarWidget(QScrollArea):
    submitReplicate = Signal(ImagePromptContainer)
    submitReplicateAllComplete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__directory = CONFIG_MANAGER.get_replicate_property('directory')
        self.__api_key = CONFIG_MANAGER.get_replicate_property('REPLICATE_API_TOKEN')
        self.__model = CONFIG_MANAGER.get_replicate_property('model')
        self.__width = CONFIG_MANAGER.get_replicate_property('width')
        self.__height = CONFIG_MANAGER.get_replicate_property('height')
        self.__prompt = CONFIG_MANAGER.get_replicate_property('prompt')
        self.__negative_prompt = CONFIG_MANAGER.get_replicate_property('negative_prompt')
        self.__is_save = CONFIG_MANAGER.get_replicate_property('is_save')
        self.__continue_generation = CONFIG_MANAGER.get_replicate_property('continue_generation')
        self.__number_of_images_to_create = CONFIG_MANAGER.get_replicate_property('number_of_images_to_create')
        self.__save_prompt_as_text = CONFIG_MANAGER.get_replicate_property('save_prompt_as_text')

        self.__wrapper = ReplicateWrapper(self.__api_key.strip() if self.__api_key else '')

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
        if sender == self.__apiKeyLineEdit:
            v = v.strip() if v else ''
            self.__api_key = v
            CONFIG_MANAGER.set_replicate_property('REPLICATE_API_TOKEN', v)
            self.__wrapper.set_api(v)
        elif sender == self.__widthSpinBox:
            self.__width = v
            CONFIG_MANAGER.set_replicate_property('width', v)
        elif sender == self.__heightSpinBox:
            self.__height = v
            CONFIG_MANAGER.set_replicate_property('height', v)

    def __replicateTextChanged(self):
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            if sender == self.__modelTextEdit:
                self.__model = sender.toPlainText()
                CONFIG_MANAGER.set_replicate_property('model', self.__model)
            elif sender == self.__promptWidget:
                self.__prompt = sender.toPlainText()
                CONFIG_MANAGER.set_replicate_property('prompt', self.__prompt)
            elif sender == self.__negativePromptWidget:
                self.__negative_prompt = sender.toPlainText()
                CONFIG_MANAGER.set_replicate_property('negative_prompt', self.__negative_prompt)

    def __setSaveDirectory(self, directory):
        self.__directory = directory
        CONFIG_MANAGER.set_replicate_property('directory', directory)

    def __saveChkBoxToggled(self, f):
        self.__is_save = f
        CONFIG_MANAGER.set_replicate_property('is_save', f)

    def __continueGenerationChkBoxToggled(self, f):
        self.__continue_generation = f
        CONFIG_MANAGER.set_replicate_property('continue_generation', f)
        self.__numberOfImagesToCreateSpinBox.setEnabled(f)

    def __numberOfImagesToCreateSpinBoxValueChanged(self, value):
        self.__number_of_images_to_create = value
        CONFIG_MANAGER.set_replicate_property('number_of_images_to_create', value)

    def __savePromptAsTextChkBoxToggled(self, f):
        self.__save_prompt_as_text = f
        CONFIG_MANAGER.set_replicate_property('save_prompt_as_text', f)

    def __submit(self):
        arg = {
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
        informative_text = 'Error 😥'
        detailed_text = event
        if not self.isVisible() or not self.window().isActiveWindow():
            self.__notifierWidget = NotifierWidget(informative_text=informative_text, detailed_text = detailed_text)
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.__bringWindowToFront)
        else:
            QMessageBox.critical(self, informative_text, detailed_text)

    def __bringWindowToFront(self):
        window = self.window()
        window.showNormal()
        window.raise_()
        window.activateWindow()

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

