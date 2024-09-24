from PySide6.QtCore import Signal, QThread
from PySide6.QtWidgets import QMessageBox, QScrollArea, QWidget, QCheckBox, QSpinBox, QGroupBox, QVBoxLayout, \
    QPushButton, QPlainTextEdit

from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.util.script import getSeparator
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.randomImagePromptGeneratorWidget import RandomImagePromptGeneratorWidget


class ImageControlWidget(QScrollArea):
    submit = Signal(ImagePromptContainer)
    submitAllComplete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initVal()
        self._initUi()

    def _initVal(self):
        self._prompt = ''
        self._continue_generation = False
        self._save_prompt_as_text = False
        self._is_save = False
        self._directory = False
        self._number_of_images_to_create = 1

    def _initUi(self):
        self._findPathWidget = FindPathWidget()
        self._findPathWidget.setAsDirectory(True)
        self._findPathWidget.getLineEdit().setPlaceholderText(LangClass.TRANSLATIONS['Choose Directory to Save...'])
        self._findPathWidget.getLineEdit().setText(self._directory)
        self._findPathWidget.added.connect(self._setSaveDirectory)

        self._saveChkBox = QCheckBox(LangClass.TRANSLATIONS['Save After Submit'])
        self._saveChkBox.setChecked(True)
        self._saveChkBox.toggled.connect(self._saveChkBoxToggled)
        self._saveChkBox.setChecked(self._is_save)

        self._numberOfImagesToCreateSpinBox = QSpinBox()
        self._numberOfImagesToCreateSpinBox.setRange(2, 1000)
        self._numberOfImagesToCreateSpinBox.setValue(self._number_of_images_to_create)
        self._numberOfImagesToCreateSpinBox.valueChanged.connect(self._numberOfImagesToCreateSpinBoxValueChanged)

        self._continueGenerationChkBox = QCheckBox(LangClass.TRANSLATIONS['Continue Image Generation'])
        self._continueGenerationChkBox.setChecked(True)
        self._continueGenerationChkBox.toggled.connect(self._continueGenerationChkBoxToggled)
        self._continueGenerationChkBox.setChecked(self._continue_generation)

        self._savePromptAsTextChkBox = QCheckBox(LangClass.TRANSLATIONS['Save Prompt as Text'])
        self._savePromptAsTextChkBox.setChecked(True)
        self._savePromptAsTextChkBox.toggled.connect(self._savePromptAsTextChkBoxToggled)
        self._savePromptAsTextChkBox.setChecked(self._save_prompt_as_text)

        self._generalGrpBox = QGroupBox()
        self._generalGrpBox.setTitle(LangClass.TRANSLATIONS['General'])

        self._promptTextEdit = QPlainTextEdit()
        self._promptTextEdit.setPlaceholderText(LangClass.TRANSLATIONS['Enter prompt here...'])
        self._promptTextEdit.setPlainText(self._prompt)

        self._randomImagePromptGeneratorWidget = RandomImagePromptGeneratorWidget()

        self._paramGrpBox = QGroupBox()
        self._paramGrpBox.setTitle(LangClass.TRANSLATIONS['Parameters'])

        self._submitBtn = QPushButton(LangClass.TRANSLATIONS['Submit'])
        self._submitBtn.clicked.connect(self._submit)

        self._stopGeneratingImageBtn = QPushButton(LangClass.TRANSLATIONS['Stop Generating Image'])
        self._stopGeneratingImageBtn.clicked.connect(self._stopGeneratingImage)
        self._stopGeneratingImageBtn.setEnabled(False)

    def _completeUi(self):
        sep = getSeparator('horizontal')

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

    def _setThread(self, thread: QThread):
        self._t = thread

    def _submit(self):
        self._t.start()
        self._t.started.connect(self._toggleWidget)
        self._t.replyGenerated.connect(self._afterGenerated)
        self._t.errorGenerated.connect(self._failToGenerate)
        self._t.finished.connect(self._toggleWidget)
        self._t.allReplyGenerated.connect(self.submitAllComplete)

    def _toggleWidget(self):
        f = not self._t.isRunning()
        continue_generation = self._continue_generation
        self._generalGrpBox.setEnabled(f)
        self._submitBtn.setEnabled(f)
        if continue_generation:
            self._stopGeneratingImageBtn.setEnabled(not f)

    def _stopGeneratingImage(self):
        if self._t.isRunning():
            self._t.stop()

    def _failToGenerate(self, event):
        informative_text = 'Error 😥'
        detailed_text = event
        if not self.isVisible() or not self.window().isActiveWindow():
            self._notifierWidget = NotifierWidget(informative_text=informative_text, detailed_text = detailed_text)
            self._notifierWidget.show()
            self._notifierWidget.doubleClicked.connect(self._bringWindowToFront)
        else:
            QMessageBox.critical(self, informative_text, detailed_text)

    def _bringWindowToFront(self):
        window = self.window()
        window.showNormal()
        window.raise_()
        window.activateWindow()

    def _afterGenerated(self, result):
        self.submit.emit(result)

    def getArgument(self):
        return {
            "prompt": self._promptTextEdit.toPlainText(),
        }

    def _setSaveDirectory(self, directory):
        self._directory = directory

    def _saveChkBoxToggled(self, f):
        self._is_save = f

    def _continueGenerationChkBoxToggled(self, f):
        self._continue_generation = f
        self._numberOfImagesToCreateSpinBox.setEnabled(f)

    def _savePromptAsTextChkBoxToggled(self, f):
        self._save_prompt_as_text = f

    def _numberOfImagesToCreateSpinBoxValueChanged(self, value):
        self._number_of_images_to_create = value

    def getSavePromptAsText(self):
        return self._save_prompt_as_text

    def isSavedEnabled(self):
        return self._is_save

    def getDirectory(self):
        return self._directory