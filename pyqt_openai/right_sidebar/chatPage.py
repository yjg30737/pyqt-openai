from qtpy.QtCore import Qt, Signal, QSettings
from qtpy.QtWidgets import QWidget, QDoubleSpinBox, QSpinBox, QFormLayout, QFrame, QSizePolicy, QComboBox, QTextEdit, QLabel, QVBoxLayout, QCheckBox, QPushButton

from pyqt_openai.pyqt_openai_data import get_chat_model
from pyqt_openai.res.language_dict import LangClass


class ChatPage(QWidget):
    onToggleLlama = Signal(bool)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)

        # default value of each properties based on https://platform.openai.com/docs/api-reference/chat/create
        # param
        if not self.__settings_ini.contains('stream'):
            self.__settings_ini.setValue('stream', True)
        if not self.__settings_ini.contains('model'):
            self.__settings_ini.setValue('model', 'gpt-4o')
        if not self.__settings_ini.contains('system'):
            self.__settings_ini.setValue('system', 'You are a helpful assistant.')
        if not self.__settings_ini.contains('temperature'):
            self.__settings_ini.setValue('temperature', 1)
        if not self.__settings_ini.contains('max_tokens'):
            self.__settings_ini.setValue('max_tokens', -1)
        if not self.__settings_ini.contains('top_p'):
            self.__settings_ini.setValue('top_p', 1)
        if not self.__settings_ini.contains('frequency_penalty'):
            self.__settings_ini.setValue('frequency_penalty', 0)
        if not self.__settings_ini.contains('presence_penalty'):
            self.__settings_ini.setValue('presence_penalty', 0)

        # etc
        if not self.__settings_ini.contains('use_max_tokens'):
            self.__settings_ini.setValue('use_max_tokens', False)
        if not self.__settings_ini.contains('use_llama_index'):
            self.__settings_ini.setValue('use_llama_index', False)

        self.__stream = self.__settings_ini.value('stream', type=bool)
        self.__model = self.__settings_ini.value('model', type=str)
        self.__system = self.__settings_ini.value('system', type=str)
        self.__temperature = self.__settings_ini.value('temperature', type=float)
        self.__max_tokens = self.__settings_ini.value('max_tokens', type=int)
        self.__top_p = self.__settings_ini.value('top_p', type=float)
        self.__frequency_penalty = self.__settings_ini.value('frequency_penalty', type=float)
        self.__presence_penalty = self.__settings_ini.value('presence_penalty', type=float)

        self.__use_max_tokens = self.__settings_ini.value('use_max_tokens', type=bool)
        self.__use_llama_index = self.__settings_ini.value('use_llama_index', type=bool)

    def __initUi(self):
        systemlbl = QLabel(LangClass.TRANSLATIONS['System'])

        self.__systemTextEdit = QTextEdit()
        self.__systemTextEdit.setText(self.__system)
        self.__systemTextEdit.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        saveSystemBtn = QPushButton(LangClass.TRANSLATIONS['Save System'])
        saveSystemBtn.clicked.connect(self.__saveSystem)

        modelCmbBox = QComboBox()
        modelCmbBox.addItems(get_chat_model())
        modelCmbBox.setCurrentText(self.__model)
        modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        temperatureSpinBox = QDoubleSpinBox()
        temperatureSpinBox.setRange(0, 2)
        temperatureSpinBox.setAccelerated(True)
        temperatureSpinBox.setSingleStep(0.01)
        temperatureSpinBox.setValue(self.__temperature)
        temperatureSpinBox.valueChanged.connect(self.__temperatureChanged)

        self.__maxTokensSpinBox = QSpinBox()
        self.__maxTokensSpinBox.setRange(1, 2048)
        self.__maxTokensSpinBox.setAccelerated(True)
        self.__maxTokensSpinBox.setValue(self.__max_tokens)
        self.__maxTokensSpinBox.valueChanged.connect(self.__maxTokensChanged)

        toppSpinBox = QDoubleSpinBox()
        toppSpinBox.setRange(0, 1)
        toppSpinBox.setAccelerated(True)
        toppSpinBox.setSingleStep(0.01)
        toppSpinBox.setValue(self.__top_p)
        toppSpinBox.valueChanged.connect(self.__toppChanged)

        frequencyPenaltySpinBox = QDoubleSpinBox()
        frequencyPenaltySpinBox.setRange(0, 2)
        frequencyPenaltySpinBox.setAccelerated(True)
        frequencyPenaltySpinBox.setSingleStep(0.01)
        frequencyPenaltySpinBox.setValue(self.__frequency_penalty)
        frequencyPenaltySpinBox.valueChanged.connect(self.__frequencyPenaltyChanged)

        presencePenaltySpinBox = QDoubleSpinBox()
        presencePenaltySpinBox.setRange(0, 2)
        presencePenaltySpinBox.setAccelerated(True)
        presencePenaltySpinBox.setSingleStep(0.01)
        presencePenaltySpinBox.setValue(self.__presence_penalty)
        presencePenaltySpinBox.valueChanged.connect(self.__presencePenaltyChanged)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText(LangClass.TRANSLATIONS['Stream'])

        llamaChkBox = QCheckBox()
        llamaChkBox.setChecked(self.__use_llama_index)
        llamaChkBox.toggled.connect(self.__use_llama_indexChecked)
        llamaChkBox.setText(LangClass.TRANSLATIONS['Use LlamaIndex'])

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        useMaxTokenChkBox = QCheckBox()
        useMaxTokenChkBox.toggled.connect(self.__useMaxChecked)
        useMaxTokenChkBox.setChecked(self.__use_max_tokens)
        useMaxTokenChkBox.setText(LangClass.TRANSLATIONS['Use Max Tokens'])
        self.__maxTokensSpinBox.setEnabled(self.__use_max_tokens)

        lay = QFormLayout()

        lay.addRow('temperature', temperatureSpinBox)
        lay.addRow('maxTokens', self.__maxTokensSpinBox)
        lay.addRow('topp', toppSpinBox)
        lay.addRow('frequencyPenalty', frequencyPenaltySpinBox)
        lay.addRow('presencePenalty', presencePenaltySpinBox)
        lay.setContentsMargins(0, 0, 0, 0)

        paramWidget = QWidget()
        paramWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(systemlbl)
        lay.addWidget(self.__systemTextEdit)
        lay.addWidget(saveSystemBtn)
        lay.addWidget(modelCmbBox)
        lay.addWidget(streamChkBox)
        lay.addWidget(useMaxTokenChkBox)
        lay.addWidget(llamaChkBox)
        lay.addWidget(sep)
        lay.addWidget(paramWidget)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

    def __saveSystem(self):
        self.__system = self.__systemTextEdit.toPlainText()
        self.__settings_ini.setValue('system', self.__system)

    def __modelChanged(self, v):
        self.__model = v
        self.__settings_ini.setValue('model', v)

    def __streamChecked(self, f):
        self.__stream = f
        self.__settings_ini.setValue('stream', f)

    def __use_llama_indexChecked(self, f):
        self.__use_llama_index = f
        self.__settings_ini.setValue('use_llama_index', f)
        self.onToggleLlama.emit(f)

    def __useMaxChecked(self, f):
        self.__use_max_tokens = f
        self.__settings_ini.setValue('use_max_tokens', f)
        self.__maxTokensSpinBox.setEnabled(f)

    def __temperatureChanged(self, v):
        self.__temperature = v
        self.__settings_ini.setValue('temperature', v)

    def __maxTokensChanged(self, v):
        self.__max_tokens = v
        self.__settings_ini.setValue('max_tokens', v)

    def __toppChanged(self, v):
        self.__top_p = v
        self.__settings_ini.setValue('top_p', v)

    def __frequencyPenaltyChanged(self, v):
        self.__frequency_penalty = v
        self.__settings_ini.setValue('frequency_penalty', v)

    def __presencePenaltyChanged(self, v):
        self.__presence_penalty = v
        self.__settings_ini.setValue('presence_penalty', v)
