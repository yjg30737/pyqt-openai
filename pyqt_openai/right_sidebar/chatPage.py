from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox, QFormLayout
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QSizePolicy, QComboBox, QTextEdit, QLabel, QVBoxLayout, QCheckBox, QPushButton

from pyqt_openai.apiData import getChatModel
from pyqt_openai.sqlite import SqliteDatabase


class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        # default value of each properties based on https://platform.openai.com/docs/api-reference/chat/create
        # param
        if not self.__settings_ini.contains('stream'):
            self.__settings_ini.setValue('stream', True)
        if not self.__settings_ini.contains('model'):
            self.__settings_ini.setValue('model', 'gpt-3.5-turbo')
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
        if not self.__settings_ini.contains('finish_reason'):
            self.__settings_ini.setValue('finish_reason', False)

        self.__stream = self.__settings_ini.value('stream', type=bool)
        self.__model = self.__settings_ini.value('model', type=str)
        self.__system = self.__settings_ini.value('system', type=str)
        self.__temperature = self.__settings_ini.value('temperature', type=float)
        self.__max_tokens = self.__settings_ini.value('max_tokens', type=int)
        self.__top_p = self.__settings_ini.value('top_p', type=float)
        self.__frequency_penalty = self.__settings_ini.value('frequency_penalty', type=float)
        self.__presence_penalty = self.__settings_ini.value('presence_penalty', type=float)

        self.__use_max_tokens = self.__settings_ini.value('use_max_tokens', type=bool)
        self.__finish_reason = self.__settings_ini.value('finish_reason', type=bool)

    def __initUi(self):
        systemlbl = QLabel('System')

        self.__systemTextEdit = QTextEdit()
        self.__systemTextEdit.setText(self.__system)
        self.__systemTextEdit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        saveSystemBtn = QPushButton('Save System')
        saveSystemBtn.clicked.connect(self.__saveSystem)

        modelCmbBox = QComboBox()
        modelCmbBox.addItems(getChatModel())
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
        streamChkBox.setText('Stream')

        useMaxTokenChkBox = QCheckBox()
        useMaxTokenChkBox.toggled.connect(self.__useMaxChecked)
        useMaxTokenChkBox.setChecked(self.__use_max_tokens)
        useMaxTokenChkBox.setText('Use Max Tokens')
        self.__maxTokensSpinBox.setEnabled(self.__use_max_tokens)

        finishReasonChkBox = QCheckBox('Show Finish Reason (working)')
        finishReasonChkBox.setChecked(self.__finish_reason)
        finishReasonChkBox.toggled.connect(self.__finishReasonChecked)
        finishReasonChkBox.setText('Show Finish Reason')

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
        lay.addWidget(finishReasonChkBox)
        lay.addWidget(paramWidget)
        lay.setAlignment(Qt.AlignTop)

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

    def __useMaxChecked(self, f):
        self.__use_max_tokens = f
        self.__settings_ini.setValue('use_max_tokens', f)
        self.__maxTokensSpinBox.setEnabled(f)

    def __finishReasonChecked(self, f):
        self.__finish_reason = f
        self.__settings_ini.setValue('finish_reason', f)

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
