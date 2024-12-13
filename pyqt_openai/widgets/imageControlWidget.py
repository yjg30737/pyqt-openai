from __future__ import annotations

from typing import TYPE_CHECKING, cast

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QCheckBox, QGroupBox, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.util.common import getSeparator
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.randomImagePromptGeneratorWidget import RandomImagePromptGeneratorWidget

if TYPE_CHECKING:
    from pyqt_openai.dalle_widget.dalleThread import DallEThread
    from pyqt_openai.g4f_image_widget.g4fImageThread import G4FImageThread
    from pyqt_openai.replicate_widget.replicateThread import ReplicateThread


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
        self._prompt: str = ""
        self._continue_generation: bool = False
        self._save_prompt_as_text: bool = False
        self._is_save: bool = False
        self._directory: bool | str = False
        self._number_of_images_to_create: int = 1
        self._t: DallEThread | G4FImageThread | ReplicateThread | None = None

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

        self._generalGrpBox: QGroupBox = QGroupBox()
        self._generalGrpBox.setTitle(LangClass.TRANSLATIONS["General"])

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

    def _setThread(
        self,
        thread: DallEThread | G4FImageThread | ReplicateThread,
    ):
        self._t = thread

    def _submit(self):
        assert self._t is not None
        self._t.start()
        self._t.started.connect(self._toggleWidget)
        self._t.replyGenerated.connect(self._afterGenerated)
        self._t.errorGenerated.connect(self._failToGenerate)
        self._t.finished.connect(self._toggleWidget)
        self._t.allReplyGenerated.connect(self.submitAllComplete)

    def _toggleWidget(self):
        assert self._t is not None
        f = not self._t.isRunning()
        continue_generation = self._continue_generation
        self._generalGrpBox.setEnabled(f)
        self._submitBtn.setEnabled(f)
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

    def getArgument(self) -> dict[str, str]:
        return {
            "prompt": self._promptTextEdit.toPlainText(),
        }

    def _setSaveDirectory(
        self,
        directory: str,
    ):
        self._directory = directory

    def _saveChkBoxToggled(
        self,
        f: bool,
    ):
        self._is_save = f

    def _continueGenerationChkBoxToggled(
        self,
        f: bool,
    ):
        self._continue_generation = f
        self._numberOfImagesToCreateSpinBox.setEnabled(f)

    def _savePromptAsTextChkBoxToggled(
        self,
        f: bool,
    ):
        self._save_prompt_as_text = f

    def _numberOfImagesToCreateSpinBoxValueChanged(
        self,
        value: int,
    ):
        self._number_of_images_to_create = value

    def getSavePromptAsText(self) -> bool:
        return self._save_prompt_as_text

    def isSavedEnabled(self) -> bool:
        return self._is_save

    def getDirectory(self) -> bool | str:
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
