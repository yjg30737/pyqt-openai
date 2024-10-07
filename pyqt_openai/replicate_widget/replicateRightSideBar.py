from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QSpinBox, QVBoxLayout, \
    QPlainTextEdit, \
    QFormLayout, QLabel, QSplitter, QPushButton

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.replicate_widget.replicateThread import ReplicateThread
from pyqt_openai.settings_dialog.settingsDialog import SettingsDialog
from pyqt_openai.widgets.imageControlWidget import ImageControlWidget


class ReplicateRightSideBarWidget(ImageControlWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        super()._initVal()

        self._prompt = CONFIG_MANAGER.get_replicate_property('prompt')
        self._continue_generation = CONFIG_MANAGER.get_replicate_property('continue_generation')
        self._save_prompt_as_text = CONFIG_MANAGER.get_replicate_property('save_prompt_as_text')
        self._is_save = CONFIG_MANAGER.get_replicate_property('is_save')
        self._directory = CONFIG_MANAGER.get_replicate_property('directory')
        self._number_of_images_to_create = CONFIG_MANAGER.get_replicate_property('number_of_images_to_create')

        self.__model = CONFIG_MANAGER.get_replicate_property('model')
        self.__width = CONFIG_MANAGER.get_replicate_property('width')
        self.__height = CONFIG_MANAGER.get_replicate_property('height')
        self.__negative_prompt = CONFIG_MANAGER.get_replicate_property('negative_prompt')

    def _initUi(self):
        super()._initUi()

        # TODO LANGUAGE
        self.__setApiBtn = QPushButton('Set API Key')
        self.__setApiBtn.clicked.connect(lambda _: SettingsDialog(default_index=1, parent=self).exec_())
        self.__setApiBtn.setStyleSheet('''
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 16px;
                    font-family: "Arial";
                    font-weight: bold;
                    border: 2px solid #007BFF;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                    border-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #003f7f;
                    border-color: #003f7f;
                }
                '''
                                )

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
        lay.addWidget(self.__setApiBtn)
        lay.addWidget(self._findPathWidget)
        lay.addWidget(self._saveChkBox)
        lay.addWidget(self._continueGenerationChkBox)
        lay.addWidget(self._numberOfImagesToCreateSpinBox)
        lay.addWidget(self._savePromptAsTextChkBox)
        self._generalGrpBox.setLayout(lay)

        self._promptTextEdit.textChanged.connect(self.__replicateTextChanged)

        self._negativeTextEdit = QPlainTextEdit()
        self._negativeTextEdit.setPlaceholderText('ugly, deformed, noisy, blurry, distorted')
        self._negativeTextEdit.setPlainText(self.__negative_prompt)
        self._negativeTextEdit.textChanged.connect(self.__replicateTextChanged)

        lay = QVBoxLayout()

        lay.addWidget(self._randomImagePromptGeneratorWidget)
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Prompt']))
        lay.addWidget(self._promptTextEdit)

        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Negative Prompt']))
        lay.addWidget(self._negativeTextEdit)
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
        if sender == self.__widthSpinBox:
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
            elif sender == self._promptTextEdit:
                self._prompt = sender.toPlainText()
                CONFIG_MANAGER.set_replicate_property('prompt', self._prompt)
            elif sender == self._negativeTextEdit:
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
        random_prompt = self._randomImagePromptGeneratorWidget.getRandomPromptSourceArr()

        t = ReplicateThread(arg, number_of_images, self.__model, random_prompt)
        self._setThread(t)
        super()._submit()

    def getArgument(self):
        obj = super().getArgument()
        return {
            **obj,
            "prompt": self._promptTextEdit.toPlainText(),
            "negative_prompt": self._negativeTextEdit.toPlainText(),
            "width": self.__width,
            "height": self.__height,
        }

