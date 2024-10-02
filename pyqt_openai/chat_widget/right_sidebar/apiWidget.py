from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QHeaderView, QTableWidgetItem, QLabel, QLineEdit, \
    QDialogButtonBox, QWidget, QPushButton

from pyqt_openai import HOW_TO_GET_OPENAI_API_KEY_URL, HOW_TO_GET_CLAUDE_API_KEY_URL, HOW_TO_GET_GEMINI_API_KEY_URL, \
    HOW_TO_GET_LLAMA_API_KEY_URL, DEFAULT_API_CONFIGS
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.globals import set_api_key
from pyqt_openai.widgets.linkLabel import LinkLabel


# FIXME Are there any ways to get authentification from the claude, gemini?
# def is_api_key_valid(endpoint, api_key):
#     response = requests.get(endpoint, headers={'Authorization': f'Bearer {api_key}'})
#     f = response.status_code == 200
#     print(f)


class ApiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__api_keys = []
        # Get the api keys from the conf file with the env var name
        for conf in DEFAULT_API_CONFIGS:
            _conf = {
                'display_name': conf['display_name'],
                'env_var_name': conf['env_var_name'],
                'api_key': CONFIG_MANAGER.get_general_property(conf['env_var_name'])
            }
            self.__api_keys.append(_conf)

        # Set "get api key" here
        for i, obj in enumerate(self.__api_keys):
            obj['get_api_key'] = {
                'OpenAI': HOW_TO_GET_OPENAI_API_KEY_URL,
                'Claude': HOW_TO_GET_CLAUDE_API_KEY_URL,
                'Gemini': HOW_TO_GET_GEMINI_API_KEY_URL,
                'Llama': HOW_TO_GET_LLAMA_API_KEY_URL
            }[obj['display_name']]

    def __initUi(self):
        self.setWindowTitle('API Key')

        columns = ['Provider', 'API Key', 'Get API Key']
        self.__tableWidget = QTableWidget()
        self.__tableWidget.setColumnCount(len(columns))
        self.__tableWidget.setHorizontalHeaderLabels(columns)
        self.__tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.__tableWidget.verticalHeader().setVisible(False)

        for i, obj in enumerate(self.__api_keys):
            self.__tableWidget.insertRow(i)
            modelItem = QTableWidgetItem(obj['display_name'])
            self.__tableWidget.setItem(i, 0, modelItem)

            apiKeyLineEdit = QLineEdit(obj['api_key'])
            apiKeyLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.__tableWidget.setCellWidget(i, 1, apiKeyLineEdit)

            getApiKeyLbl = LinkLabel()
            getApiKeyLbl.setText('Link')
            getApiKeyLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            getApiKeyLbl.setUrl(obj['get_api_key'])
            self.__tableWidget.setCellWidget(i, 2, getApiKeyLbl)

        saveBtn = QPushButton('Save')
        saveBtn.clicked.connect(self.setApiKeys)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('API Key'))
        lay.addWidget(self.__tableWidget)
        lay.addWidget(saveBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self.setMinimumHeight(150)

    def setApiKeys(self):
        """
        Dynamically get the api keys from the table widget
        """
        api_keys = {self.__api_keys[i]['env_var_name']: self.__tableWidget.cellWidget(i, 1).text() for i in range(self.__tableWidget.rowCount())}
        # Save the api keys to the conf file
        for k, v in api_keys.items():
            CONFIG_MANAGER.set_general_property(k, v)
            set_api_key(k, v)