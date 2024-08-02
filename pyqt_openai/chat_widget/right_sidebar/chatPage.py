from qtpy.QtCore import Qt, Signal, QSettings
from qtpy.QtWidgets import QWidget, QDoubleSpinBox, QSpinBox, QFormLayout, QSizePolicy, QComboBox, QTextEdit, \
    QLabel, QVBoxLayout, QCheckBox, QPushButton, QScrollArea, QGroupBox

from pyqt_openai import INI_FILE_NAME, DEFAULT_SHORTCUT_JSON_MODE, OPENAI_TEMPERATURE_RANGE, OPENAI_TEMPERATURE_STEP, \
    MAX_TOKENS_RANGE, TOP_P_RANGE, TOP_P_STEP, FREQUENCY_PENALTY_RANGE, PRESENCE_PENALTY_STEP, PRESENCE_PENALTY_RANGE, \
    FREQUENCY_PENALTY_STEP
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.pyqt_openai_data import get_chat_model, LLAMAINDEX_WRAPPER
from pyqt_openai.util.script import getSeparator


class ChatPage(QWidget):
    onToggleLlama = Signal(bool)
    onToggleJSON = Signal(bool)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings(INI_FILE_NAME, QSettings.Format.IniFormat)

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
        if not self.__settings_ini.contains('json_object'):
            self.__settings_ini.setValue('json_object', False)

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
        self.__json_object = self.__settings_ini.value('json_object', type=bool)

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

        advancedSettingsScrollArea = QScrollArea()

        self.__temperatureSpinBox = QDoubleSpinBox()
        self.__temperatureSpinBox.setRange(*OPENAI_TEMPERATURE_RANGE)
        self.__temperatureSpinBox.setAccelerated(True)
        self.__temperatureSpinBox.setSingleStep(OPENAI_TEMPERATURE_STEP)
        self.__temperatureSpinBox.setValue(self.__temperature)
        self.__temperatureSpinBox.valueChanged.connect(self.__valueChanged)

        self.__maxTokensSpinBox = QSpinBox()
        self.__maxTokensSpinBox.setRange(*MAX_TOKENS_RANGE)
        self.__maxTokensSpinBox.setAccelerated(True)
        self.__maxTokensSpinBox.setValue(self.__max_tokens)
        self.__maxTokensSpinBox.valueChanged.connect(self.__valueChanged)

        self.__toppSpinBox = QDoubleSpinBox()
        self.__toppSpinBox.setRange(*TOP_P_RANGE)
        self.__toppSpinBox.setAccelerated(True)
        self.__toppSpinBox.setSingleStep(TOP_P_STEP)
        self.__toppSpinBox.setValue(self.__top_p)
        self.__toppSpinBox.valueChanged.connect(self.__valueChanged)

        self.__frequencyPenaltySpinBox = QDoubleSpinBox()
        self.__frequencyPenaltySpinBox.setRange(*FREQUENCY_PENALTY_RANGE)
        self.__frequencyPenaltySpinBox.setAccelerated(True)
        self.__frequencyPenaltySpinBox.setSingleStep(FREQUENCY_PENALTY_STEP)
        self.__frequencyPenaltySpinBox.setValue(self.__frequency_penalty)
        self.__frequencyPenaltySpinBox.valueChanged.connect(self.__valueChanged)

        self.__presencePenaltySpinBox = QDoubleSpinBox()
        self.__presencePenaltySpinBox.setRange(*PRESENCE_PENALTY_RANGE)
        self.__presencePenaltySpinBox.setAccelerated(True)
        self.__presencePenaltySpinBox.setSingleStep(PRESENCE_PENALTY_STEP)
        self.__presencePenaltySpinBox.setValue(self.__presence_penalty)
        self.__presencePenaltySpinBox.valueChanged.connect(self.__valueChanged)

        lay = QFormLayout()

        lay.addRow('temperature', self.__temperatureSpinBox)
        lay.addRow('maxTokens', self.__maxTokensSpinBox)
        lay.addRow('topp', self.__toppSpinBox)
        lay.addRow('frequencyPenalty', self.__frequencyPenaltySpinBox)
        lay.addRow('presencePenalty', self.__presencePenaltySpinBox)

        paramWidget = QWidget()
        paramWidget.setLayout(lay)

        advancedSettingsScrollArea.setWidgetResizable(True)
        advancedSettingsScrollArea.setWidget(paramWidget)

        lay = QVBoxLayout()
        lay.addWidget(advancedSettingsScrollArea)

        advancedSettingsGrpBox = QGroupBox(LangClass.TRANSLATIONS['Advanced Settings'])
        advancedSettingsGrpBox.setLayout(lay)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText(LangClass.TRANSLATIONS['Stream'])

        jsonChkBox = QCheckBox()
        jsonChkBox.setChecked(self.__json_object)
        jsonChkBox.toggled.connect(self.__jsonObjectChecked)

        jsonChkBox.setText(LangClass.TRANSLATIONS['Enable JSON mode'])
        jsonChkBox.setShortcut(DEFAULT_SHORTCUT_JSON_MODE)
        jsonChkBox.setToolTip(LangClass.TRANSLATIONS['When enabled, you can send a JSON object to the API and the response will be in JSON format. Otherwise, it will be in plain text.'])

        llamaChkBox = QCheckBox()
        llamaChkBox.setChecked(self.__use_llama_index)
        llamaChkBox.toggled.connect(self.__use_llama_indexChecked)
        llamaChkBox.setText(LangClass.TRANSLATIONS['Use LlamaIndex'])

        useMaxTokenChkBox = QCheckBox()
        useMaxTokenChkBox.toggled.connect(self.__useMaxChecked)
        useMaxTokenChkBox.setChecked(self.__use_max_tokens)
        useMaxTokenChkBox.setText(LangClass.TRANSLATIONS['Use Max Tokens'])
        self.__maxTokensSpinBox.setEnabled(self.__use_max_tokens)

        sep = getSeparator('horizontal')

        lay = QVBoxLayout()
        lay.addWidget(systemlbl)
        lay.addWidget(self.__systemTextEdit)
        lay.addWidget(saveSystemBtn)
        lay.addWidget(modelCmbBox)
        lay.addWidget(streamChkBox)
        lay.addWidget(jsonChkBox)
        lay.addWidget(useMaxTokenChkBox)
        lay.addWidget(llamaChkBox)
        lay.addWidget(sep)
        lay.addWidget(advancedSettingsGrpBox)
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

    def __jsonObjectChecked(self, f):
        self.__json_object = f
        self.__settings_ini.setValue('json_object', f)
        self.onToggleJSON.emit(f)

    def __use_llama_indexChecked(self, f):
        self.__use_llama_index = f
        self.__settings_ini.setValue('use_llama_index', f)
        if f:
            # Set llama index directory if it exists
            if self.__settings_ini.contains('llama_index_directory') and self.__settings_ini.value(
                    'use_llama_index', False, type=bool):
                LLAMAINDEX_WRAPPER.set_directory(self.__settings_ini.value('llama_index_directory'))
        self.onToggleLlama.emit(f)

    def __useMaxChecked(self, f):
        self.__use_max_tokens = f
        self.__settings_ini.setValue('use_max_tokens', f)
        self.__maxTokensSpinBox.setEnabled(f)

    def __valueChanged(self, v):
        sender = self.sender()
        if sender == self.__temperatureSpinBox:
            self.__temperature = v
            self.__settings_ini.setValue('temperature', v)
        elif sender == self.__maxTokensSpinBox:
            self.__max_tokens = v
            self.__settings_ini.setValue('max_tokens', v)
        elif sender == self.__toppSpinBox:
            self.__top_p = v
            self.__settings_ini.setValue('top_p', v)
        elif sender == self.__frequencyPenaltySpinBox:
            self.__frequency_penalty = v
            self.__settings_ini.setValue('frequency_penalty', v)
        elif sender == self.__presencePenaltySpinBox:
            self.__presence_penalty = v
            self.__settings_ini.setValue('presence_penalty', v)
