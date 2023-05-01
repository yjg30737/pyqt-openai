import platform, subprocess

from qtpy.QtGui import QFont
from qtpy.QtWidgets import QWidget, QComboBox, QTextEdit, QLabel, QVBoxLayout, QApplication, QCheckBox, QDoubleSpinBox, \
    QSpinBox, QFormLayout, QHBoxLayout, QFileDialog, QPushButton, QLineEdit, QGroupBox
from qtpy.QtCore import Qt, QSettings

from pyqt_openai.apiData import getCompletionModel, getLatestModel
from pyqt_openai.modelTable import ModelTable
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgLabel import SvgLabel


class CompletionPage(QWidget):
    def __init__(self, db: SqliteDatabase, ini_etc_dict, model_data):
        super().__init__()
        self.__initVal(db, ini_etc_dict, model_data)
        self.__initUi()

    def __setChatInfo(self, db):
        self.__db = db

        self.__info_dict = self.__db.selectInfo(2)

    def __initVal(self, db, ini_etc_dict, model_data):
        self.__setChatInfo(db)
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        self.__modelData = model_data
        self.__ini_etc_dict = ini_etc_dict

    def __initUi(self):
        self.__modelComboBox = QComboBox()
        self.__modelComboBox.addItems(getCompletionModel())
        self.__modelComboBox.setCurrentText(self.__info_dict['engine'])
        self.__modelComboBox.currentTextChanged.connect(self.__modelChanged)

        self.__fineTuningBtn = QPushButton('Fine Tuning')
        self.__fineTuningBtn.clicked.connect(self.__fineTuning)

        # find the training data
        self.__findDataLineEdit = QLineEdit()

        seeEveryModelCheckBox = QCheckBox('View every model (not all models may work)')
        seeEveryModelCheckBox.toggled.connect(self.__seeEveryModelToggled)
        seeEveryModelCheckBoxLbl = SvgLabel()
        seeEveryModelCheckBoxLbl.setSvgFile('ico/help.svg')
        seeEveryModelCheckBoxLbl.setToolTip(
            '''Check this box to show all models, including obsolete ones. If you don\'t check this, combobox lists <a href="https://platform.openai.com/docs/models/gpt-3-5">latest models.</a>''')
        seeEveryModelCheckBoxLbl.installEventFilter(self)

        lay = QHBoxLayout()
        lay.addWidget(seeEveryModelCheckBox)
        lay.addWidget(seeEveryModelCheckBoxLbl)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignLeft)

        seeEveryModelWidget = QWidget()
        seeEveryModelWidget.setLayout(lay)

        temperatureSpinBox = QDoubleSpinBox()
        temperatureSpinBox.setRange(0, 1)
        temperatureSpinBox.setAccelerated(True)
        temperatureSpinBox.setSingleStep(0.01)
        temperatureSpinBox.setValue(self.__info_dict['temperature'])
        temperatureSpinBox.valueChanged.connect(self.__temperatureChanged)

        maxTokensSpinBox = QSpinBox()
        maxTokensSpinBox.setRange(0, 4000)
        maxTokensSpinBox.setAccelerated(True)
        maxTokensSpinBox.setValue(self.__info_dict['max_tokens'])
        maxTokensSpinBox.valueChanged.connect(self.__maxTokensChanged)

        toppSpinBox = QDoubleSpinBox()
        toppSpinBox.setRange(0, 1)
        toppSpinBox.setAccelerated(True)
        toppSpinBox.setSingleStep(0.01)
        toppSpinBox.setValue(self.__info_dict['top_p'])
        toppSpinBox.valueChanged.connect(self.__toppChanged)

        frequencyPenaltySpinBox = QDoubleSpinBox()
        frequencyPenaltySpinBox.setRange(0, 2)
        frequencyPenaltySpinBox.setAccelerated(True)
        frequencyPenaltySpinBox.setSingleStep(0.01)
        frequencyPenaltySpinBox.setValue(self.__info_dict['frequency_penalty'])
        frequencyPenaltySpinBox.valueChanged.connect(self.__frequencyPenaltyChanged)

        presencePenaltySpinBox = QDoubleSpinBox()
        presencePenaltySpinBox.setRange(0, 2)
        presencePenaltySpinBox.setAccelerated(True)
        presencePenaltySpinBox.setSingleStep(0.01)
        # presencePenaltySpinBox.setValue(self.__info_dict['presence_penalty'])
        # presencePenaltySpinBox.valueChanged.connect(self.__presencePenaltyChanged)

        modelTableSubLbl = QLabel('You can view the information only by entering the valid API key.')
        modelTableSubLbl.setFont(QFont('Arial', 9))

        self.__apiCheckPreviewLbl = QLabel('')
        self.__modelTable = ModelTable()

        lay = QVBoxLayout()
        lay.addWidget(modelTableSubLbl)
        lay.addWidget(self.__modelTable)

        modelTableGrpBox = QGroupBox()
        modelTableGrpBox.setTitle('Model Info (testing)')
        modelTableGrpBox.setLayout(lay)

        lay = QFormLayout()
        lay.addWidget(seeEveryModelWidget)
        lay.addRow('Model', self.__modelComboBox)
        lay.addRow(modelTableGrpBox)
        lay.addRow('Temperature', temperatureSpinBox)
        lay.addRow('Maximum length', maxTokensSpinBox)
        lay.addRow('Top P', toppSpinBox)
        lay.addRow('Frequency penalty', frequencyPenaltySpinBox)
        lay.addRow('Presence penalty', presencePenaltySpinBox)

        modelOptionGrpBox = QGroupBox()
        modelOptionGrpBox.setTitle('Model')
        modelOptionGrpBox.setLayout(lay)

        rememberPastConversationChkBox = QCheckBox('Store Previous Conversation in Real Time (testing)')
        rememberPastConversationChkBox.setChecked(self.__ini_etc_dict['remember_past_conv'])
        rememberPastConversationChkBox.setDisabled(True)
        rememberPastConversationChkBox.toggled.connect(self.__rememberPastConversationChkBoxToggled)

        lay = QVBoxLayout()
        lay.addWidget(rememberPastConversationChkBox)

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
        lay.addWidget(optionGrpBox)
        lay.addWidget(fineTuneGrpBox)

        self.setLayout(lay)

    def __temperatureChanged(self, v):
        self.__temperature = round(v, 2)
        self.__db.updateInfo(2, 'temperature', v)

    def __maxTokensChanged(self, v):
        self.__max_tokens = round(v, 2)
        self.__db.updateInfo(2, 'max_tokens', v)

    def __toppChanged(self, v):
        self.__topp = round(v, 2)
        self.__db.updateInfo(2, 'top_p', v)

    def __frequencyPenaltyChanged(self, v):
        self.__frequency_penalty = round(v, 2)
        self.__db.updateInfo(2, 'frequency_penalty', v)

    def __presencePenaltyChanged(self, v):
        self.__presence_penalty = round(v, 2)
        self.__db.updateInfo(2, 'presence_penalty', v)

    def __seeEveryModelToggled(self, f):
        curModel = self.__modelComboBox.currentText()
        self.__modelComboBox.currentTextChanged.disconnect(self.__modelChanged)
        self.__modelComboBox.clear()
        if f:
            self.__modelComboBox.addItems([model.id for model in self.__modelData.getModelData()])
        else:
            self.__modelComboBox.addItems(getCompletionModel())
        self.__modelComboBox.currentTextChanged.connect(self.__modelChanged)
        self.__modelComboBox.setCurrentText(curModel)

    # for fine-tuning, showing the detailed information of the model
    def setModelInfoByModel(self, init_model: bool = False):
        if init_model:
            self.__modelData.setModelData()
        self.__modelTable.setModelInfo(self.__modelData.getModelData(), self.__info_dict['engine'], 'allow_fine_tuning')
        self.__fineTuningBtn.setEnabled(self.__modelTable.getModelInfo())

    def __findData(self):
        filename = QFileDialog.getOpenFileName(self, 'Open', '', 'JSONL Files (*.jsonl)')
        if filename[0]:
            filename = filename[0]
            self.__findDataLineEdit.setText(filename)
            self.__fineTuningBtn.setEnabled(True)

    def __fineTuning(self):
        if platform.system() == 'Windows':
            subprocess.Popen('cmd.exe', creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif platform.system() in ['Darwin', 'Linux']:
            subprocess.Popen('bash', creationflags=subprocess.CREATE_NEW_CONSOLE)

        # https://platform.openai.com/docs/guides/fine-tuning/cli-data-preparation-tool
        # validating & giving suggestions and reformat the data
        # subprocess.run('openai tools fine_tunes.prepare_data -f data.jsonl')

        # https://platform.openai.com/docs/guides/fine-tuning/create-a-fine-tuned-model
        # create a fine-tuned model
        # subprocess.run('openai api fine_tunes.create -t [TRAIN_FILE_ID_OR_PATH] -m [BASE_MODEL]')

        # run this when event stream is interrupted for any reason
        # subprocess.run('openai api fine_tunes.follow -i [YOUR_FINE_TUNE_JOB_ID]')
        # you can see the job done when it is finished
        # https://platform.openai.com/account/usage
        # https://platform.openai.com/playground

        # list the jobs
        # subprocess.run('openai api fine_tunes.list')

        # get the status of certain job. The resulting object includes
        # job status (which can be one of pending, running, succeeded, or failed)
        # and other information
        # subprocess.run('openai api fine_tunes.get -i [YOUR_FINE_TUNE_JOB_ID]')

        # cancel the job
        # subprocess.run('openai api fine_tunes.cancel -i [YOUR_FINE_TUNE_JOB_ID]')

    def __modelChanged(self, v):
        self.__info_dict['engine'] = v
        self.setModelInfoByModel()
        self.__db.updateInfo(2, 'engine', v)

    def __rememberPastConversationChkBoxToggled(self, f):
        self.__settings_struct.setValue('REMEMBER_PAST_CONVERSATION', str(int(f)))