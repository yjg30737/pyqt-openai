from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QSizePolicy, QComboBox, QTextEdit, QLabel, QVBoxLayout, QCheckBox, QPushButton

from pyqt_openai.apiData import getChatModel
from pyqt_openai.sqlite import SqliteDatabase


class ChatPage(QWidget):
    def __init__(self, db: SqliteDatabase, ini_etc_dict):
        super().__init__()
        self.__initVal(db, ini_etc_dict)
        self.__initUi()

    def __setChatInfo(self, db):
        self.__db = db
        self.__info_dict = self.__db.selectInfo(1)

        # # set each field as variable since these are being used a lot
        # model = info_dict['model']
        # temperature = info_dict['temperature']
        # max_tokens = info_dict['max_tokens']
        # top_p = info_dict['top_p']
        # frequency_penalty = info_dict['frequency_penalty']
        # presence_penalty = info_dict['presence_penalty']
        # stream = info_dict['stream']

        # set each field as variable since these are being used a lot
        self.__stream = self.__info_dict.get('stream', False)

    def __initVal(self, db, ini_etc_dict):
        self.__setChatInfo(db)
        self.__ini_etc_dict = ini_etc_dict

    def __initUi(self):
        systemlbl = QLabel('System')
        self.__systemTextEdit = QTextEdit()
        self.__systemTextEdit.setText('You are a helpful assistant.')
        self.__systemTextEdit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        saveSystemBtn = QPushButton('Save System')
        saveSystemBtn.clicked.connect(self.__saveSystem)
        modelCmbBox = QComboBox()
        modelCmbBox.addItems(getChatModel())
        modelCmbBox.setCurrentText(self.__info_dict['model'])
        modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        # temperatureSpinBox = QDoubleSpinBox()
        # temperatureSpinBox.setRange(0, 1)
        # temperatureSpinBox.setAccelerated(True)
        # temperatureSpinBox.setSingleStep(0.01)
        # # temperatureSpinBox.setValue(self.__info_dict['temperature'])
        # # temperatureSpinBox.valueChanged.connect(self.__temperatureChanged)
        #
        # # later
        # # maxTokensSpinBox = QSpinBox()
        # # maxTokensSpinBox.setRange(0, 4000)
        # # maxTokensSpinBox.setAccelerated(True)
        # # maxTokensSpinBox.setValue(self.__info_dict['max_tokens'])
        # # maxTokensSpinBox.valueChanged.connect(self.__maxTokensChanged)
        #
        # toppSpinBox = QDoubleSpinBox()
        # toppSpinBox.setRange(0, 1)
        # toppSpinBox.setAccelerated(True)
        # toppSpinBox.setSingleStep(0.01)
        # # toppSpinBox.setValue(self.__info_dict['top_p'])
        # # toppSpinBox.valueChanged.connect(self.__toppChanged)
        #
        # frequencyPenaltySpinBox = QDoubleSpinBox()
        # frequencyPenaltySpinBox.setRange(0, 2)
        # frequencyPenaltySpinBox.setAccelerated(True)
        # frequencyPenaltySpinBox.setSingleStep(0.01)
        # # frequencyPenaltySpinBox.setValue(self.__info_dict['frequency_penalty'])
        # # frequencyPenaltySpinBox.valueChanged.connect(self.__frequencyPenaltyChanged)
        #
        # presencePenaltySpinBox = QDoubleSpinBox()
        # presencePenaltySpinBox.setRange(0, 2)
        # presencePenaltySpinBox.setAccelerated(True)
        # presencePenaltySpinBox.setSingleStep(0.01)
        # # presencePenaltySpinBox.setValue(self.__info_dict['presence_penalty'])
        # # presencePenaltySpinBox.valueChanged.connect(self.__presencePenaltyChanged)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText('Stream')

        finishReasonChkBox = QCheckBox('Show Finish Reason (working)')
        finishReasonChkBox.setChecked(self.__ini_etc_dict['finishReason'])
        finishReasonChkBox.toggled.connect(self.__finishReasonChecked)
        finishReasonChkBox.setText('Show Finish Reason')

        lay = QVBoxLayout()
        lay.addWidget(systemlbl)
        lay.addWidget(self.__systemTextEdit)
        lay.addWidget(saveSystemBtn)
        lay.addWidget(modelCmbBox)
        lay.addWidget(streamChkBox)
        lay.addWidget(finishReasonChkBox)
        lay.setAlignment(Qt.AlignTop)

        self.setLayout(lay)

    def __saveSystem(self):
        self.__info_dict['system'] = self.__systemTextEdit.toPlainText()
        self.__db.updateInfo(1, 'system', self.__info_dict['system'])

    def __modelChanged(self, v):
        self.__info_dict['model'] = v
        # self.setModelInfoByModel()
        self.__db.updateInfo(1, 'model', v)

    def __streamChecked(self, f):
        self.__stream = f
        self.__db.updateInfo(1, 'stream', f)

    def __finishReasonChecked(self, f):
        self.__finishReason = f