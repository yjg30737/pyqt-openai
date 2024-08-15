import requests
from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QFont, QColor
from qtpy.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QLabel, QWidget

from pyqt_openai import OPENAI_REQUEST_URL
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.pyqt_openai_data import setOpenAIEnabled, setApiKeyAndClientGlobal


class ApiWidget(QWidget):
    onAIEnabled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        apiLbl = QLabel(LangClass.TRANSLATIONS['API'])

        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText(LangClass.TRANSLATIONS['Write your API Key...'])
        self.__apiLineEdit.returnPressed.connect(self.setApi)
        self.__apiLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        apiBtn = QPushButton(LangClass.TRANSLATIONS['Use'])
        apiBtn.clicked.connect(self.setApi)

        # TODO LANGUAGE
        self.__openaiApiManualLbl = QLabel('You can get your API key from https://platform.openai.com/account/api-keys')
        self.__openaiApiManualLbl.setOpenExternalLinks(True)

        lay = QHBoxLayout()
        lay.addWidget(apiLbl)
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(apiBtn)
        lay.addWidget(self.__apiCheckPreviewLbl)
        lay.addWidget(self.__openaiApiManualLbl)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setLayout(lay)

    def setApiKeyAndClient(self, api_key):
        setApiKeyAndClientGlobal(api_key)

        # for showing to the user
        self.__apiLineEdit.setText(api_key)

    def setApi(self):
        try:
            api_key = self.__apiLineEdit.text()
            response = requests.get(OPENAI_REQUEST_URL, headers={'Authorization': f'Bearer {api_key}'})
            f = setOpenAIEnabled(response.status_code == 200)
            self.onAIEnabled.emit(f)
            if f:
                self.setApiKeyAndClient(api_key)
                CONFIG_MANAGER.set_general_property('API_KEY', api_key)

                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(0, 200, 0).name()))
                self.__apiCheckPreviewLbl.setText(LangClass.TRANSLATIONS['API key is valid'])
            else:
                raise Exception
        except Exception as e:
            self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(255, 0, 0).name()))
            self.__apiCheckPreviewLbl.setText(LangClass.TRANSLATIONS['API key is invalid'])
            self.onAIEnabled.emit(False)
            print(e)
        finally:
            self.__apiCheckPreviewLbl.show()

    def showApiCheckPreviewLbl(self, f):
        self.__apiCheckPreviewLbl.show() if f else self.__apiCheckPreviewLbl.hide()