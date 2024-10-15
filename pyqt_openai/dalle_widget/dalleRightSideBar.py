from PySide6.QtWidgets import (
    QSpinBox,
    QGroupBox,
    QVBoxLayout,
    QComboBox,
    QPlainTextEdit,
    QFormLayout,
    QLabel,
    QRadioButton,
)

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.dalle_widget.dalleThread import DallEThread
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.imageControlWidget import ImageControlWidget
from pyqt_openai.widgets.modernButton import ModernButton


class DallERightSideBarWidget(ImageControlWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        super()._initVal()

        self._prompt = CONFIG_MANAGER.get_dalle_property("prompt")
        self._continue_generation = CONFIG_MANAGER.get_dalle_property(
            "continue_generation"
        )
        self._save_prompt_as_text = CONFIG_MANAGER.get_dalle_property(
            "save_prompt_as_text"
        )
        self._is_save = CONFIG_MANAGER.get_dalle_property("is_save")
        self._directory = CONFIG_MANAGER.get_dalle_property("directory")
        self._number_of_images_to_create = CONFIG_MANAGER.get_dalle_property(
            "number_of_images_to_create"
        )

        self.__quality = CONFIG_MANAGER.get_dalle_property("quality")
        self.__n = CONFIG_MANAGER.get_dalle_property("n")
        self.__size = CONFIG_MANAGER.get_dalle_property("size")
        self.__style = CONFIG_MANAGER.get_dalle_property("style")
        self.__response_format = CONFIG_MANAGER.get_dalle_property("response_format")
        self.__prompt_type = CONFIG_MANAGER.get_dalle_property("prompt_type")
        self.__width = CONFIG_MANAGER.get_dalle_property("width")
        self.__height = CONFIG_MANAGER.get_dalle_property("height")

    def _initUi(self):
        super()._initUi()

        # TODO LANGUAGE
        self.__setApiBtn = ModernButton()
        self.__setApiBtn.setText("Set API Key")

        self.__promptTypeToShowRadioGrpBox = QGroupBox(
            LangClass.TRANSLATIONS["Prompt Type To Show"]
        )

        self.__normalOne = QRadioButton(LangClass.TRANSLATIONS["Normal"])
        self.__revisedOne = QRadioButton(LangClass.TRANSLATIONS["Revised"])

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

        lay = QVBoxLayout()
        lay.addWidget(self.__setApiBtn)
        lay.addWidget(self._findPathWidget)
        lay.addWidget(self._saveChkBox)
        lay.addWidget(self._continueGenerationChkBox)
        lay.addWidget(self._numberOfImagesToCreateSpinBox)
        lay.addWidget(self._savePromptAsTextChkBox)
        lay.addWidget(self.__promptTypeToShowRadioGrpBox)
        self._generalGrpBox.setLayout(lay)

        self.__qualityCmbBox = QComboBox()
        self.__qualityCmbBox.addItems(["standard", "hd"])
        self.__qualityCmbBox.setCurrentText(self.__quality)
        self.__qualityCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__nSpinBox = QSpinBox()
        self.__nSpinBox.setRange(1, 10)
        self.__nSpinBox.setValue(self.__n)
        self.__nSpinBox.valueChanged.connect(self.__dalleChanged)
        self.__nSpinBox.setEnabled(False)

        self.__sizeLimitLabel = QLabel(
            LangClass.TRANSLATIONS[
                "※ Images can have a size of 1024x1024, 1024x1792 or 1792x1024 pixels."
            ]
        )
        self.__sizeLimitLabel.setWordWrap(True)

        self.__widthCmbBox = QComboBox()
        self.__widthCmbBox.addItems(["1024", "1792"])
        self.__widthCmbBox.setCurrentText(str(self.__width))
        self.__widthCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__heightCmbBox = QComboBox()
        self.__heightCmbBox.addItems(["1024", "1792"])
        self.__heightCmbBox.setCurrentText(str(self.__height))
        self.__heightCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self._promptTextEdit.textChanged.connect(self.__dalleTextChanged)

        self.__styleCmbBox = QComboBox()
        self.__styleCmbBox.addItems(["vivid", "natural"])
        self.__styleCmbBox.currentTextChanged.connect(self.__dalleChanged)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS["Quality"], self.__qualityCmbBox)
        lay.addRow(LangClass.TRANSLATIONS["Total"], self.__nSpinBox)
        lay.addRow(self.__sizeLimitLabel)
        lay.addRow(LangClass.TRANSLATIONS["Width"], self.__widthCmbBox)
        lay.addRow(LangClass.TRANSLATIONS["Height"], self.__heightCmbBox)
        lay.addRow(LangClass.TRANSLATIONS["Style"], self.__styleCmbBox)

        lay.addRow(self._randomImagePromptGeneratorWidget)
        lay.addRow(QLabel(LangClass.TRANSLATIONS["Prompt"]))
        lay.addRow(self._promptTextEdit)

        self._paramGrpBox.setLayout(lay)

        self._completeUi()

    def __dalleChanged(self, v):
        sender = self.sender()
        if sender == self.__qualityCmbBox:
            self.__quality = v
            CONFIG_MANAGER.set_dalle_property("quality", self.__quality)
        elif sender == self.__nSpinBox:
            self.__n = v
            CONFIG_MANAGER.set_dalle_property("n", self.__n)
        elif sender == self.__widthCmbBox:
            if (
                self.__widthCmbBox.currentText() == "1792"
                and self.__heightCmbBox.currentText() == "1792"
            ):
                self.__heightCmbBox.setCurrentText("1024")
            self.__width = v
            CONFIG_MANAGER.set_dalle_property("width", self.__width)
        elif sender == self.__heightCmbBox:
            if (
                self.__widthCmbBox.currentText() == "1792"
                and self.__heightCmbBox.currentText() == "1792"
            ):
                self.__widthCmbBox.setCurrentText("1024")
            self.__height = v
            CONFIG_MANAGER.set_dalle_property("height", self.__height)
        elif sender == self.__styleCmbBox:
            self.__style = v
            CONFIG_MANAGER.set_dalle_property("style", self.__style)

    # TODO combine __dalleTextChanged and __replicateTextChanged and rename them to __promptTextChanged
    def __dalleTextChanged(self):
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            if sender == self._promptTextEdit:
                self._prompt = sender.toPlainText()
                CONFIG_MANAGER.set_dalle_property("prompt", self._prompt)

    def _setSaveDirectory(self, directory):
        super()._setSaveDirectory(directory)
        CONFIG_MANAGER.set_dalle_property("directory", directory)

    def _saveChkBoxToggled(self, f):
        super()._saveChkBoxToggled(f)
        CONFIG_MANAGER.set_dalle_property("is_save", f)

    def _continueGenerationChkBoxToggled(self, f):
        super()._continueGenerationChkBoxToggled(f)
        CONFIG_MANAGER.set_dalle_property("continue_generation", f)

    def _savePromptAsTextChkBoxToggled(self, f):
        super()._savePromptAsTextChkBoxToggled(f)
        CONFIG_MANAGER.set_dalle_property("save_prompt_as_text", f)

    def _numberOfImagesToCreateSpinBoxValueChanged(self, value):
        super()._numberOfImagesToCreateSpinBoxValueChanged(value)
        CONFIG_MANAGER.set_dalle_property("number_of_images_to_create", value)

    def __promptTypeToggled(self, f):
        sender = self.sender()
        # Prompt type to show on the image
        # 1 is normal, 2 is revised
        if sender == self.__normalOne:
            self.__prompt_type = 1
            CONFIG_MANAGER.set_dalle_property("prompt_type", self.__prompt_type)
        elif sender == self.__revisedOne:
            self.__prompt_type = 2
            CONFIG_MANAGER.set_dalle_property("prompt_type", self.__prompt_type)

    def _submit(self):
        arg = self.getArgument()
        number_of_images = (
            self._number_of_images_to_create if self._continue_generation else 1
        )
        random_prompt = (
            self._randomImagePromptGeneratorWidget.getRandomPromptSourceArr()
        )

        t = DallEThread(arg, number_of_images, random_prompt)
        self._setThread(t)
        super()._submit()

    def getArgument(self):
        obj = super().getArgument()
        return {
            **obj,
            "model": "dall-e-3",
            "prompt": self._promptTextEdit.toPlainText(),
            "n": self.__n,
            "size": f"{self.__width}x{self.__height}",
            "quality": self.__quality,
            "style": self.__style,
            "response_format": self.__response_format,
        }
