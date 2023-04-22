import openai
import requests
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont, QColor
from qtpy.QtWidgets import QVBoxLayout, QWidget, QComboBox, QSpinBox, \
    QFormLayout, QDoubleSpinBox, QPushButton, QHBoxLayout, QGroupBox, QLineEdit, QLabel, QCheckBox

from pyqt_openai.apiData import getLatestModel
from pyqt_openai.modelTable import ModelTable
from pyqt_openai.svgLabel import SvgLabel


class RightSideBar(QWidget):
    def __init__(self, engine, model_data):
        super().__init__()
        self.__initVal(engine, model_data)
        self.__initUi()

    def __initVal(self, engine, model_data):
        self.__engine = engine
        self.__modelData = model_data

    def __initUi(self):
        self.__modelComboBox = QComboBox()
        self.__modelComboBox.addItems(getLatestModel())
        self.__modelComboBox.setCurrentText(self.__engine)
        self.__modelComboBox.currentTextChanged.connect(self.__modelChanged)

        temperatureSpinBox = QDoubleSpinBox()
        temperatureSpinBox.setRange(0, 1)
        temperatureSpinBox.setAccelerated(True)
        temperatureSpinBox.setSingleStep(0.01)
        temperatureSpinBox.setValue(self.__temperature)
        temperatureSpinBox.valueChanged.connect(self.__temperatureChanged)

        maxTokensSpinBox = QSpinBox()
        maxTokensSpinBox.setRange(0, 4000)
        maxTokensSpinBox.setAccelerated(True)
        maxTokensSpinBox.setValue(self.__max_tokens)
        maxTokensSpinBox.valueChanged.connect(self.__maxTokensChanged)

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

        finishReasonChkBox = QCheckBox()
        finishReasonChkBox.setChecked(self.__finishReason)
        finishReasonChkBox.toggled.connect(self.__finishReasonChecked)
        finishReasonChkBox.setText('Show Finish Reason')

        saveAsLogButton = QPushButton('Save the Conversation as Log')
        saveAsLogButton.clicked.connect(self.__saveAsLog)

        apiLbl = QLabel('API')
        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText('Write your API Key...')
        self.__apiLineEdit.setText(openai.api_key)

        self.__apiCheckPreviewLbl = QLabel('')
        self.__modelTable = ModelTable()

        self.__fineTuningBtn = QPushButton('Fine Tuning')
        self.__fineTuningBtn.clicked.connect(self.__fineTuning)

        # TODO move this to the bottom to enhance the readability
        # check if loaded API_KEY from ini file is not empty
        if openai.api_key:
            # check if loaded api is valid
            response = requests.get('https://api.openai.com/v1/engines', headers={'Authorization': f'Bearer {openai.api_key}'})
            f = response.status_code == 200
            self.__lineEdit.setEnabled(f)
            if f:
                self.__setModelInfoByModel(True)
                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(0, 200, 0).name()))
                self.__apiCheckPreviewLbl.setText('API key is valid')
            else:
                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(255, 0, 0).name()))
                self.__apiCheckPreviewLbl.setText('API key is invalid')
            self.__apiCheckPreviewLbl.show()

        # if it is empty
        else:
            self.__lineEdit.setEnabled(False)
            self.__apiCheckPreviewLbl.hide()

        self.__apiLineEdit.returnPressed.connect(self.__setApi)
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)

        apiBtn = QPushButton('Use')
        apiBtn.clicked.connect(self.__setApi)

        lay = QHBoxLayout()
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(apiBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        apiWidget = QWidget()
        apiWidget.setLayout(lay)

        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        lay = QVBoxLayout()
        lay.addWidget(apiLbl)
        lay.addWidget(apiWidget)
        lay.addWidget(self.__apiCheckPreviewLbl)
        lay.setAlignment(Qt.AlignTop)

        apiGrpBox = QGroupBox()
        apiGrpBox.setLayout(lay)
        apiGrpBox.setFixedHeight(apiGrpBox.sizeHint().height() + self.__apiCheckPreviewLbl.fontMetrics().boundingRect('M').height())

        seeEveryModelCheckBox = QCheckBox('View every model (not all models may work)')
        seeEveryModelCheckBox.toggled.connect(self.__seeEveryModelToggled)
        seeEveryModelCheckBoxLbl = SvgLabel()
        seeEveryModelCheckBoxLbl.setSvgFile('ico/help.svg')
        seeEveryModelCheckBoxLbl.setToolTip('''Check this box to show all models, including obsolete ones. If you don\'t check this, combobox lists <a href="https://platform.openai.com/docs/models/gpt-3-5">latest models.</a>''')
        seeEveryModelCheckBoxLbl.installEventFilter(self)

        lay = QHBoxLayout()
        lay.addWidget(seeEveryModelCheckBox)
        lay.addWidget(seeEveryModelCheckBoxLbl)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignLeft)

        seeEveryModelWidget = QWidget()
        seeEveryModelWidget.setLayout(lay)

        modelTableSubLbl = QLabel('You can view the information only by entering the valid API key.')
        modelTableSubLbl.setFont(QFont('Arial', 9))

        lay = QVBoxLayout()
        lay.addWidget(modelTableSubLbl)
        lay.addWidget(self.__modelTable)

        modelTableGrpBox = QGroupBox()
        modelTableGrpBox.setTitle('Model Info (testing)')
        modelTableGrpBox.setLayout(lay)

        lay = QFormLayout()
        lay.addRow(seeEveryModelWidget)
        lay.addRow('Model', self.__modelComboBox)
        lay.addRow(modelTableGrpBox)
        lay.addRow('Temperature', temperatureSpinBox)
        lay.addRow('Maximum length', maxTokensSpinBox)
        lay.addRow('Top P', toppSpinBox)
        lay.addRow('Frequency penalty', frequencyPenaltySpinBox)
        lay.addRow('Presence penalty', presencePenaltySpinBox)
        lay.addRow(streamChkBox)
        lay.addRow(finishReasonChkBox)

        modelOptionGrpBox = QGroupBox()
        modelOptionGrpBox.setTitle('Model')
        modelOptionGrpBox.setLayout(lay)

        rememberPastConversationChkBox = QCheckBox('Store Previous Conversation in Real Time (testing)')
        rememberPastConversationChkBox.setChecked(self.__remember_past_conv)
        rememberPastConversationChkBox.setDisabled(True)
        rememberPastConversationChkBox.toggled.connect(self.__rememberPastConversationChkBoxToggled)

        lay = QVBoxLayout()
        lay.addWidget(rememberPastConversationChkBox)
        lay.addWidget(saveAsLogButton)

        generalOptionGrpBox = QGroupBox()
        generalOptionGrpBox.setTitle('General')
        generalOptionGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(modelOptionGrpBox)
        lay.addWidget(generalOptionGrpBox)
        lay.setAlignment(Qt.AlignTop)

        optionGrpBox = QGroupBox()
        optionGrpBox.setTitle('Option')
        optionGrpBox.setLayout(lay)

        # find the training data
        self.__findDataLineEdit = QLineEdit()

        findDataBtn = QPushButton('Find...')
        findDataBtn.clicked.connect(self.__findData)

        lay = QHBoxLayout()
        lay.setSpacing(0)
        lay.addWidget(self.__findDataLineEdit)
        lay.addWidget(findDataBtn)
        lay.setAlignment(Qt.AlignTop)
        lay.setContentsMargins(5, 5, 5, 1)

        fineTuneGrpBoxTopWidget = QWidget()
        fineTuneGrpBoxTopWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__fineTuningBtn)
        lay.setAlignment(Qt.AlignTop)

        fineTuneGrpBoxBottomWidget = QWidget()
        fineTuneGrpBoxBottomWidget.setLayout(lay)
        lay.setContentsMargins(5, 1, 5, 5)

        lay = QVBoxLayout()
        lay.addWidget(fineTuneGrpBoxTopWidget)
        lay.addWidget(fineTuneGrpBoxBottomWidget)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        fineTuneGrpBox = QGroupBox()
        fineTuneGrpBox.setTitle('Fine-tune training (coming soon)')
        fineTuneGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(apiGrpBox)
        lay.addWidget(optionGrpBox)
        lay.addWidget(fineTuneGrpBox)

        self.__rightSidebarWidget = QWidget()
        self.__rightSidebarWidget.setLayout(lay)

    def __seeEveryModelToggled(self, f):
        curModel = self.__modelComboBox.currentText()
        self.__modelComboBox.currentTextChanged.disconnect(self.__modelChanged)
        self.__modelComboBox.clear()
        if f:
            self.__modelComboBox.addItems([model.id for model in self.__modelData.getModelData()])
        else:
            self.__modelComboBox.addItems(getLatestModel())
        self.__modelComboBox.currentTextChanged.connect(self.__modelChanged)
        self.__modelComboBox.setCurrentText(curModel)

    def __setModelInfoByModel(self, init_model: bool = False):
        if init_model:
            self.__modelData.setModelData()
        self.__modelTable.setModelInfo(self.__modelData.getModelData(), self.__engine, 'allow_fine_tuning')
        self.__fineTuningBtn.setEnabled(self.__modelTable.getModelInfo())

    def __modelChanged(self, v):
        self.__engine = v
        self.__setModelInfoByModel()