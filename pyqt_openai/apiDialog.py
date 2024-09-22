from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QHeaderView, QTableWidgetItem, QLabel, QLineEdit, QDialog, \
    QDialogButtonBox


# FIXME Are there any ways to get authentification from the claude, gemini?
# def is_api_key_valid(endpoint, api_key):
#     response = requests.get(endpoint, headers={'Authorization': f'Bearer {api_key}'})
#     f = response.status_code == 200
#     print(f)


class ApiDialog(QDialog):
    def __init__(self, api_keys: list, parent=None):
        super().__init__(parent)
        self.__initVal(api_keys)
        self.__initUi()

    def __initVal(self, api_keys):
        self.__api_keys = api_keys

    def __initUi(self):
        columns = ['Models', 'API Key']
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

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('API Key'))
        lay.addWidget(self.__tableWidget)
        lay.addWidget(buttonBox)

        self.setLayout(lay)

        self.setMinimumWidth(600)

    def getApiKeys(self) -> dict:
        """
        Dynamically get the api keys from the table widget
        """
        api_keys = {self.__api_keys[i]['env_var_name']: self.__tableWidget.cellWidget(i, 1).text() for i in range(self.__tableWidget.rowCount())}
        return api_keys