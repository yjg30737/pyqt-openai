from __future__ import annotations

from typing import cast

from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QCheckBox, QGroupBox, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSpinBox, \
    QVBoxLayout, QWidget, QLabel, QFormLayout, QSplitter, QComboBox

from pyqt_openai import MIN_IMAGE_SIZE, MAX_IMAGE_SIZE
from pyqt_openai.chat_widget.right_sidebar.modelSearchBar import ModelSearchBar
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.util.common import getSeparator, get_image_providers, get_g4f_image_models, \
    get_g4f_image_models_from_provider, ImageThread
from pyqt_openai.widgets.APIInputButton import APIInputButton
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.randomImagePromptGeneratorWidget import RandomImagePromptGeneratorWidget


class ImageControlWidget(QScrollArea):
    submit = Signal(ImagePromptContainer)
    submitAllComplete = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        self._t = None

        self._prompt = CONFIG_MANAGER.get_image_property("prompt")
        self._continue_generation = bool(CONFIG_MANAGER.get_image_property(
            "continue_generation",
        ))
        self._save_prompt_as_text = bool(CONFIG_MANAGER.get_image_property(
            "save_prompt_as_text",
        ))
        self._is_save = bool(CONFIG_MANAGER.get_image_property("is_save"))
        self._directory = CONFIG_MANAGER.get_image_property("directory")
        self._number_of_images_to_create = CONFIG_MANAGER.get_image_property(
            "number_of_images_to_create",
        )

        self.__model = CONFIG_MANAGER.get_image_property("model")
        self.__provider = CONFIG_MANAGER.get_image_property("provider")
        self.__negative_prompt = CONFIG_MANAGER.get_image_property(
            "negative_prompt",
        )
        self.__width: int = int(CONFIG_MANAGER.get_image_property("width") or 1024)
        self.__height: int = int(CONFIG_MANAGER.get_image_property("height") or 1024)

    def _initUi(self):
        self._findPathWidget: FindPathWidget = FindPathWidget()
        self._findPathWidget.setAsDirectory(True)
        self._findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS["Choose Directory to Save..."])
        self._findPathWidget.getLineEdit().setText(cast(str, self._directory))
        self._findPathWidget.added.connect(self._setSaveDirectory)

        self._saveChkBox: QCheckBox = QCheckBox(LangClass.TRANSLATIONS["Save After Submit"])
        self._saveChkBox.setChecked(True)
        self._saveChkBox.toggled.connect(self._saveChkBoxToggled)
        self._saveChkBox.setChecked(self._is_save)

        self._numberOfImagesToCreateSpinBox: QSpinBox = QSpinBox()
        self._numberOfImagesToCreateSpinBox.setRange(2, 1000)
        self._numberOfImagesToCreateSpinBox.setValue(self._number_of_images_to_create)
        self._numberOfImagesToCreateSpinBox.valueChanged.connect(self._numberOfImagesToCreateSpinBoxValueChanged)

        self._continueGenerationChkBox: QCheckBox = QCheckBox(LangClass.TRANSLATIONS["Continue Image Generation"])
        self._continueGenerationChkBox.setChecked(True)
        self._continueGenerationChkBox.toggled.connect(self._continueGenerationChkBoxToggled)
        self._continueGenerationChkBox.setChecked(self._continue_generation)

        self._savePromptAsTextChkBox: QCheckBox = QCheckBox(LangClass.TRANSLATIONS["Save Prompt as Text"])
        self._savePromptAsTextChkBox.setChecked(True)
        self._savePromptAsTextChkBox.toggled.connect(self._savePromptAsTextChkBoxToggled)
        self._savePromptAsTextChkBox.setChecked(self._save_prompt_as_text)
        self._savePromptAsTextChkBox.setEnabled(self._save_prompt_as_text)

        self.__setApiBtn = APIInputButton()
        self.__setApiBtn.setText("Set API Key")

        self._generalGrpBox: QGroupBox = QGroupBox()
        self._generalGrpBox.setTitle(LangClass.TRANSLATIONS["General"])

        self.__widthSpinBox = QSpinBox()
        self.__widthSpinBox.setRange(MIN_IMAGE_SIZE, MAX_IMAGE_SIZE)
        self.__widthSpinBox.setSingleStep(8)
        self.__widthSpinBox.setValue(self.__width)
        self.__widthSpinBox.valueChanged.connect(self.__widthHeightChanged)

        self.__heightSpinBox = QSpinBox()
        self.__heightSpinBox.setRange(MIN_IMAGE_SIZE, MAX_IMAGE_SIZE)
        self.__heightSpinBox.setSingleStep(8)
        self.__heightSpinBox.setValue(self.__height)
        self.__heightSpinBox.valueChanged.connect(self.__widthHeightChanged)

        self._promptTextEdit: QPlainTextEdit = QPlainTextEdit()
        self._promptTextEdit.setPlaceholderText(LangClass.TRANSLATIONS["Enter prompt here..."])
        self._promptTextEdit.setPlainText(self._prompt)

        self._randomImagePromptGeneratorWidget: RandomImagePromptGeneratorWidget = RandomImagePromptGeneratorWidget()

        self._paramGrpBox: QGroupBox = QGroupBox()
        self._paramGrpBox.setTitle(LangClass.TRANSLATIONS["Parameters"])

        self._submitBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["Submit"])
        self._submitBtn.clicked.connect(self._submit)

        self._stopGeneratingImageBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["Stop Generating Image"])
        self._stopGeneratingImageBtn.clicked.connect(self._stopGeneratingImage)
        self._stopGeneratingImageBtn.setEnabled(False)

        self._stopGeneratingImageBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["Stop Generating Image"])
        self._stopGeneratingImageBtn.clicked.connect(self._stopGeneratingImage)
        self._stopGeneratingImageBtn.setEnabled(False)

        sep = getSeparator("horizontal")

        lay = QVBoxLayout()
        lay.addWidget(self._generalGrpBox)
        lay.addWidget(self._paramGrpBox)
        lay.addWidget(sep)
        lay.addWidget(self._submitBtn)
        lay.addWidget(self._stopGeneratingImageBtn)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

        # Compose the detailed configuration of the Control Widget
        self.__providerCmbBox = QComboBox()
        g4f_image_providers = get_image_providers(including_auto=True)
        self.__providerCmbBox.addItems(g4f_image_providers)
        self.__providerCmbBox.currentTextChanged.connect(self.__providerChanged)

        self.__modelCmbBox = ModelSearchBar()
        g4f_image_models = get_g4f_image_models()
        self.__modelCmbBox.setChatModel(g4f_image_models)
        self.__modelCmbBox.setText(self.__model)
        self.__modelCmbBox.textChanged.connect(self.__modelChanged)

        self.__providerCmbBox.setCurrentText(self.__provider)

        lay = QVBoxLayout()
        lay.addWidget(self._findPathWidget)
        lay.addWidget(self._saveChkBox)
        lay.addWidget(self._continueGenerationChkBox)
        lay.addWidget(self._numberOfImagesToCreateSpinBox)
        lay.addWidget(self._savePromptAsTextChkBox)
        lay.addWidget(self.__setApiBtn)
        self._generalGrpBox.setLayout(lay)

        self._promptTextEdit.textChanged.connect(self.__promptChanged)

        self._negativeTextEdit = QPlainTextEdit()
        self._negativeTextEdit.setPlaceholderText(
            "ugly, deformed, noisy, blurry, distorted",
        )
        self._negativeTextEdit.setPlainText(self.__negative_prompt)
        self._negativeTextEdit.textChanged.connect(self.__promptChanged)

        lay = QVBoxLayout()

        lay.addWidget(self._randomImagePromptGeneratorWidget)
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Prompt"]))
        lay.addWidget(self._promptTextEdit)

        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Negative Prompt"]))
        lay.addWidget(self._negativeTextEdit)
        promptWidget = QWidget()
        promptWidget.setLayout(lay)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS["Provider"], self.__providerCmbBox)
        lay.addRow(LangClass.TRANSLATIONS["Model"], self.__modelCmbBox)
        lay.addRow(LangClass.TRANSLATIONS["Width"], self.__widthSpinBox)
        lay.addRow(LangClass.TRANSLATIONS["Height"], self.__heightSpinBox)
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

    def _setThread(
        self,
        thread: ImageThread,
    ):
        self._t = thread

    def _toggleWidget(self):
        assert self._t is not None
        f = not self._t.isRunning()
        continue_generation = self._continue_generation
        self._generalGrpBox.setEnabled(f)
        # self._submitBtn.setEnabled(f)
        if continue_generation:
            self._stopGeneratingImageBtn.setEnabled(not f)

    def _stopGeneratingImage(self):
        assert self._t is not None
        if self._t.isRunning():
            self._t.stop()

    def _failToGenerate(
        self,
        event: str,
    ):
        informative_text: str = "Error 😥"
        detailed_text: str = event

        window_of_self: QWidget | None = self.window()
        assert window_of_self is not None
        if window_of_self is None or not self.isVisible() or not window_of_self.isActiveWindow():
            self._notifierWidget: NotifierWidget = NotifierWidget(
                informative_text=informative_text,
                detailed_text=detailed_text,
            )
            self._notifierWidget.show()
            self._notifierWidget.doubleClicked.connect(self._bringWindowToFront)
        else:
            QMessageBox.critical(
                None,  # pyright: ignore[reportArgumentType]
                informative_text,
                detailed_text,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Cancel,
            )

    def _bringWindowToFront(self):
        window: QWidget | None = self.window()
        if window is None:
            return
        window.showNormal()
        window.raise_()
        window.activateWindow()

    def _afterGenerated(
        self,
        result: object,
    ):
        self.submit.emit(result)

    def _setSaveDirectory(
        self,
        directory: str,
    ):
        self._directory = directory
        CONFIG_MANAGER.set_image_property("directory", directory)

    def _saveChkBoxToggled(
        self,
        f: bool,
    ):
        self._is_save = f
        CONFIG_MANAGER.set_image_property("is_save", f)

    def _continueGenerationChkBoxToggled(
        self,
        f: bool,
    ):
        self._continue_generation = f
        self._numberOfImagesToCreateSpinBox.setEnabled(f)
        CONFIG_MANAGER.set_image_property("continue_generation", f)

    def _savePromptAsTextChkBoxToggled(
        self,
        f: bool,
    ):
        self._save_prompt_as_text = f
        CONFIG_MANAGER.set_image_property("save_prompt_as_text", f)

    def _numberOfImagesToCreateSpinBoxValueChanged(
        self,
        value: int,
    ):
        self._number_of_images_to_create = value
        CONFIG_MANAGER.set_image_property("number_of_images_to_create", value)

    def getSavePromptAsText(self) -> bool:
        return self._save_prompt_as_text

    def isSavedEnabled(self) -> bool:
        return self._is_save

    def getDirectory(self) -> str:
        return self._directory

    def _completeUi(self):
        """Complete the UI setup after all widgets have been initialized."""
        mainWidget = QWidget()
        lay = QVBoxLayout()
        lay.addWidget(self._generalGrpBox)
        lay.addWidget(self._paramGrpBox)
        lay.addWidget(getSeparator("horizontal"))
        lay.addWidget(self._submitBtn)
        lay.addWidget(self._stopGeneratingImageBtn)
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def __modelChanged(self, text):
        self.__model = text
        CONFIG_MANAGER.set_image_property("model", self.__model)

    def __providerChanged(self, text):
        self.__provider = text
        CONFIG_MANAGER.set_image_property("provider", self.__provider)

        image_models = get_g4f_image_models_from_provider(self.__provider)
        self.__modelCmbBox.clear()
        self.__modelCmbBox.setChatModel(image_models)

    def __widthHeightChanged(self):
        sender = self.sender()
        if isinstance(sender, QSpinBox):
            if sender == self.__widthSpinBox:
                self.__width = sender.value()
                CONFIG_MANAGER.set_image_property("width", self.__width)
            elif sender == self.__heightSpinBox:
                self.__height = sender.value()
                CONFIG_MANAGER.set_image_property("height", self.__height)

    def __promptChanged(self):
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            if sender == self._promptTextEdit:
                self._prompt = sender.toPlainText()
                CONFIG_MANAGER.set_image_property("prompt", self._prompt)
            elif sender == self._negativeTextEdit:
                self.__negative_prompt = sender.toPlainText()
                CONFIG_MANAGER.set_image_property(
                    "negative_prompt", self.__negative_prompt,
                )

    def _submit(self):
        arg = self.getArgument()
        number_of_images = (
            self._number_of_images_to_create if self._continue_generation else 1
        )
        random_prompt = (
            self._randomImagePromptGeneratorWidget.getRandomPromptSourceArr()
        )

        t = ImageThread(arg, number_of_images, random_prompt)
        self._setThread(t)

        self._t.start()
        self._t.started.connect(self._toggleWidget)
        self._t.replyGenerated.connect(self._afterGenerated)
        self._t.errorGenerated.connect(self._failToGenerate)
        self._t.finished.connect(self._toggleWidget)
        self._t.allReplyGenerated.connect(self.submitAllComplete)

    def getArgument(self):
        return {
            "prompt": self._promptTextEdit.toPlainText(),
            "model": self.__modelCmbBox.text(),
            "provider": self.__providerCmbBox.currentText(),
            "negative_prompt": self._negativeTextEdit.toPlainText(),
            "width": self.__width,
            "height": self.__height,
        }