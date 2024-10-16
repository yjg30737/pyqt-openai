from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QFormLayout,
    QLabel,
    QSplitter, QComboBox,
)

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.g4f_image_widget.g4fImageThread import G4FImageThread
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.imageControlWidget import ImageControlWidget


class G4FImageRightSideBarWidget(ImageControlWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        super()._initVal()

        self._prompt = CONFIG_MANAGER.get_g4f_image_property("prompt")
        self._continue_generation = CONFIG_MANAGER.get_g4f_image_property(
            "continue_generation"
        )
        self._save_prompt_as_text = CONFIG_MANAGER.get_g4f_image_property(
            "save_prompt_as_text"
        )
        self._is_save = CONFIG_MANAGER.get_g4f_image_property("is_save")
        self._directory = CONFIG_MANAGER.get_g4f_image_property("directory")
        self._number_of_images_to_create = CONFIG_MANAGER.get_g4f_image_property(
            "number_of_images_to_create"
        )

        self.__model = CONFIG_MANAGER.get_g4f_image_property("model")
        self.__negative_prompt = CONFIG_MANAGER.get_g4f_image_property(
            "negative_prompt"
        )

    def _initUi(self):
        super()._initUi()

        # TODO add registered image models in g4f to combobox
        self.__modelCmbBox = QComboBox()
        self.__modelCmbBox.addItems([self.__model])
        self.__modelCmbBox.setCurrentText(self.__model)
        self.__modelCmbBox.currentTextChanged.connect(self.__g4fModelChanged)

        lay = QVBoxLayout()
        lay.addWidget(self._findPathWidget)
        lay.addWidget(self._saveChkBox)
        lay.addWidget(self._continueGenerationChkBox)
        lay.addWidget(self._numberOfImagesToCreateSpinBox)
        lay.addWidget(self._savePromptAsTextChkBox)
        self._generalGrpBox.setLayout(lay)

        self._promptTextEdit.textChanged.connect(self.__replicateTextChanged)

        self._negativeTextEdit = QPlainTextEdit()
        self._negativeTextEdit.setPlaceholderText(
            "ugly, deformed, noisy, blurry, distorted"
        )
        self._negativeTextEdit.setPlainText(self.__negative_prompt)
        self._negativeTextEdit.textChanged.connect(self.__replicateTextChanged)

        lay = QVBoxLayout()

        lay.addWidget(self._randomImagePromptGeneratorWidget)
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Prompt"]))
        lay.addWidget(self._promptTextEdit)

        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Negative Prompt"]))
        lay.addWidget(self._negativeTextEdit)
        promptWidget = QWidget()
        promptWidget.setLayout(lay)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS["Model"], self.__modelCmbBox)
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

    def __g4fModelChanged(self, text):
        self.__model = text
        CONFIG_MANAGER.set_g4f_image_property("model", self.__model)

    def __replicateTextChanged(self):
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            if sender == self._promptTextEdit:
                self._prompt = sender.toPlainText()
                CONFIG_MANAGER.set_g4f_image_property("prompt", self._prompt)
            elif sender == self._negativeTextEdit:
                self.__negative_prompt = sender.toPlainText()
                CONFIG_MANAGER.set_g4f_image_property(
                    "negative_prompt", self.__negative_prompt
                )

    def _setSaveDirectory(self, directory):
        super()._setSaveDirectory(directory)
        CONFIG_MANAGER.set_g4f_image_property("directory", directory)

    def _saveChkBoxToggled(self, f):
        super()._saveChkBoxToggled(f)
        CONFIG_MANAGER.set_g4f_image_property("is_save", f)

    def _continueGenerationChkBoxToggled(self, f):
        super()._continueGenerationChkBoxToggled(f)
        CONFIG_MANAGER.set_g4f_image_property("continue_generation", f)

    def _savePromptAsTextChkBoxToggled(self, f):
        super()._savePromptAsTextChkBoxToggled(f)
        CONFIG_MANAGER.set_g4f_image_property("save_prompt_as_text", f)

    def _numberOfImagesToCreateSpinBoxValueChanged(self, value):
        super()._numberOfImagesToCreateSpinBoxValueChanged(value)
        CONFIG_MANAGER.set_g4f_image_property("number_of_images_to_create", value)

    def _submit(self):
        arg = self.getArgument()
        number_of_images = (
            self._number_of_images_to_create if self._continue_generation else 1
        )
        random_prompt = (
            self._randomImagePromptGeneratorWidget.getRandomPromptSourceArr()
        )

        t = G4FImageThread(arg, number_of_images, self.__model, random_prompt)
        self._setThread(t)
        super()._submit()

    def getArgument(self):
        obj = super().getArgument()
        return {
            **obj,
            "model": self.__modelCmbBox.currentText(),
            "prompt": self._promptTextEdit.toPlainText(),
            "negative_prompt": self._negativeTextEdit.toPlainText(),
        }
