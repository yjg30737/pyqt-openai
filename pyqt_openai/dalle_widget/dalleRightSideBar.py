from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qtpy.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLabel, QPlainTextEdit, QRadioButton, QSpinBox, QVBoxLayout

from pyqt_openai import OPENAI_DEFAULT_IMAGE_MODEL
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.dalle_widget.dalleThread import DallEThread
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.APIInputButton import APIInputButton
from pyqt_openai.widgets.imageControlWidget import ImageControlWidget

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class DallERightSideBarWidget(ImageControlWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        super()._initVal()

        self._prompt: str = CONFIG_MANAGER.get_dalle_property("prompt") or ""
        self._continue_generation: bool = bool(CONFIG_MANAGER.get_dalle_property("continue_generation"))
        self._save_prompt_as_text: bool = bool(CONFIG_MANAGER.get_dalle_property("save_prompt_as_text"))
        self._is_save: bool = bool(CONFIG_MANAGER.get_dalle_property("is_save"))
        self._directory: str = CONFIG_MANAGER.get_dalle_property("directory") or ""
        self._number_of_images_to_create: int = int(CONFIG_MANAGER.get_dalle_property("number_of_images_to_create") or 1)

        self.__quality: str = CONFIG_MANAGER.get_dalle_property("quality") or "standard"
        self.__n: int = int(CONFIG_MANAGER.get_dalle_property("n") or 1)
        self.__size: str = CONFIG_MANAGER.get_dalle_property("size") or "1024x1024"
        self.__style: str = CONFIG_MANAGER.get_dalle_property("style") or "vivid"
        self.__response_format: str = CONFIG_MANAGER.get_dalle_property("response_format") or "url"
        self.__prompt_type: int = int(CONFIG_MANAGER.get_dalle_property("prompt_type") or 1)
        self.__width: int = int(CONFIG_MANAGER.get_dalle_property("width") or 1024)
        self.__height: int = int(CONFIG_MANAGER.get_dalle_property("height") or 1024)

    def _initUi(self):
        super()._initUi()

        # TODO LANGUAGE
        self.__setApiBtn = APIInputButton()
        self.__setApiBtn.setText("Set API Key")

        self.__promptTypeToShowRadioGrpBox = QGroupBox(
            LangClass.TRANSLATIONS["Prompt Type To Show"],
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
        self.__qualityCmbBox.setCurrentText(self.__quality or "standard")
        self.__qualityCmbBox.currentTextChanged.connect(self.__dalleChanged)

        self.__nSpinBox = QSpinBox()
        self.__nSpinBox.setRange(1, 10)
        self.__nSpinBox.setValue(int(self.__n or 1))
        self.__nSpinBox.valueChanged.connect(self.__dalleChanged)
        self.__nSpinBox.setEnabled(False)

        self.__sizeLimitLabel = QLabel(
            LangClass.TRANSLATIONS[
                "※ Images can have a size of 1024x1024, 1024x1792 or 1792x1024 pixels."
            ],
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

    def _setSaveDirectory(self, directory: str):
        super()._setSaveDirectory(directory)
        CONFIG_MANAGER.set_dalle_property("directory", directory)

    def _saveChkBoxToggled(self, f: bool):
        super()._saveChkBoxToggled(f)
        CONFIG_MANAGER.set_dalle_property("is_save",f)

    def _continueGenerationChkBoxToggled(self, f: bool):
        super()._continueGenerationChkBoxToggled(f)
        CONFIG_MANAGER.set_dalle_property("continue_generation",f)

    def _savePromptAsTextChkBoxToggled(self, f: bool):
        super()._savePromptAsTextChkBoxToggled(f)
        CONFIG_MANAGER.set_dalle_property("save_prompt_as_text",f)

    def _numberOfImagesToCreateSpinBoxValueChanged(self, value: int):
        super()._numberOfImagesToCreateSpinBoxValueChanged(value)
        CONFIG_MANAGER.set_dalle_property("number_of_images_to_create",value)

    def __promptTypeToggled(self, f: bool):
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

    def getArgument(self) -> dict[str, Any]:
        obj = super().getArgument()
        return {
            **obj,
            "model": OPENAI_DEFAULT_IMAGE_MODEL,
            "prompt": self._promptTextEdit.toPlainText(),
            "n": self.__n,
            "size": f"{self.__width}x{self.__height}",
            "quality": self.__quality,
            "style": self.__style,
            "response_format": self.__response_format,
        }
