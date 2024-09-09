from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QWidget, QSpinBox, QVBoxLayout, \
    QPlainTextEdit, \
    QFormLayout, QLabel, QSplitter

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.replicate_widget.replicateThread import ReplicateThread
from pyqt_openai.util.replicate_script import ReplicateWrapper
from pyqt_openai.widgets.imageControlWidget import ImageControlWidget


class ReplicateRightSideBarWidget(ImageControlWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        super()._initVal()

        self._continue_generation = CONFIG_MANAGER.get_replicate_property('continue_generation')
        self._save_prompt_as_text = CONFIG_MANAGER.get_replicate_property('save_prompt_as_text')
        self._is_save = CONFIG_MANAGER.get_replicate_property('is_save')
        self._directory = CONFIG_MANAGER.get_replicate_property('directory')
        self._number_of_images_to_create = CONFIG_MANAGER.get_replicate_property('number_of_images_to_create')

        self.__api_key = CONFIG_MANAGER.get_replicate_property('REPLICATE_API_TOKEN')
        self.__model = CONFIG_MANAGER.get_replicate_property('model')
        self.__width = CONFIG_MANAGER.get_replicate_property('width')
        self.__height = CONFIG_MANAGER.get_replicate_property('height')
        self.__prompt = CONFIG_MANAGER.get_replicate_property('prompt')
        self.__negative_prompt = CONFIG_MANAGER.get_replicate_property('negative_prompt')

        self.__wrapper = ReplicateWrapper(self.__api_key.strip() if self.__api_key else '')

    def _initUi(self):
        super()._initUi()

        self.__apiKeyLineEdit = QLineEdit()
        self.__apiKeyLineEdit.setPlaceholderText(LangClass.TRANSLATIONS['Enter Replicate API Key...'])
        self.__apiKeyLineEdit.setText(self.__api_key)
        self.__apiKeyLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.__apiKeyLineEdit.textChanged.connect(self.__replicateChanged)

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

        lay = QVBoxLayout()
        lay.addWidget(self.__apiKeyLineEdit)
        lay.addWidget(self._findPathWidget)
        lay.addWidget(self._saveChkBox)
        lay.addWidget(self._continueGenerationChkBox)
        lay.addWidget(self._numberOfImagesToCreateSpinBox)
        lay.addWidget(self._savePromptAsTextChkBox)
        self._generalGrpBox.setLayout(lay)

        self.__promptWidget = QPlainTextEdit()
        self.__promptWidget.setPlainText(self.__prompt)
        self.__promptWidget.textChanged.connect(self.__replicateTextChanged)
        self.__promptWidget.setPlaceholderText(LangClass.TRANSLATIONS['Enter prompt here...'])

        self.__negativePromptWidget = QPlainTextEdit()
        self.__negativePromptWidget.setPlaceholderText('ugly, deformed, noisy, blurry, distorted')
        self.__negativePromptWidget.setPlainText(self.__negative_prompt)
        self.__negativePromptWidget.textChanged.connect(self.__replicateTextChanged)

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
        self._paramGrpBox.setLayout(lay)

        self._completeUi()

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

    def _setSaveDirectory(self, directory):
        super()._setSaveDirectory(directory)
        CONFIG_MANAGER.set_replicate_property('directory', directory)

    def _saveChkBoxToggled(self, f):
        super()._saveChkBoxToggled(f)
        CONFIG_MANAGER.set_replicate_property('is_save', f)

    def _continueGenerationChkBoxToggled(self, f):
        super()._continueGenerationChkBoxToggled(f)
        CONFIG_MANAGER.set_replicate_property('continue_generation', f)

    def _savePromptAsTextChkBoxToggled(self, f):
        super()._savePromptAsTextChkBoxToggled(f)
        CONFIG_MANAGER.set_replicate_property('save_prompt_as_text', f)

    def _numberOfImagesToCreateSpinBoxValueChanged(self, value):
        super()._numberOfImagesToCreateSpinBoxValueChanged(value)
        CONFIG_MANAGER.set_replicate_property('number_of_images_to_create', value)

    def _submit(self):
        arg = self.getArgument()
        number_of_images = self._number_of_images_to_create if self._continue_generation else 1

        self.__api_key = self.__apiKeyLineEdit.text().strip()
        self.__wrapper.set_api(self.__api_key)

        t = ReplicateThread(self.__wrapper, self.__model, arg, number_of_images)
        self._setThread(t)
        super()._submit()

    def getArgument(self):
        return {
            "prompt": self.__promptWidget.toPlainText(),
            "negative_prompt": self.__negativePromptWidget.toPlainText(),
            "width": self.__width,
            "height": self.__height,
        }

