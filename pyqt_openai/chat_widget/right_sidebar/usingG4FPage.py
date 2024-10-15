from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QComboBox,
    QCheckBox,
    QFormLayout,
    QTextBrowser,
    QSizePolicy,
)

from pyqt_openai import G4F_PROVIDER_DEFAULT
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import (
    get_g4f_providers,
    get_g4f_models_by_provider,
    get_chat_model,
    get_g4f_models,
    getSeparator,
)


class UsingG4FPage(QWidget):
    onToggleLlama = Signal(bool)
    onToggleJSON = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__stream = CONFIG_MANAGER.get_general_property("stream")
        self.__model = CONFIG_MANAGER.get_general_property("g4f_model")
        self.__provider = CONFIG_MANAGER.get_general_property("provider")

    def __initUi(self):
        manualBrowser = QTextBrowser()
        manualBrowser.setOpenExternalLinks(True)
        manualBrowser.setOpenLinks(True)

        # TODO LANGUAGE
        manualBrowser.setHtml(
            """
        <h2>Using GPT4Free (Free)</h2>
        <h3>Description</h3>
        <p>- Responses may often be slow or incomplete.</p>
        <p>- The response server may be unstable.</p>
        """
        )
        manualBrowser.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        self.__modelCmbBox = QComboBox()
        self.__modelCmbBox.addItems(get_chat_model(is_g4f=True))
        self.__modelCmbBox.setCurrentText(self.__model)
        self.__modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText(LangClass.TRANSLATIONS["Stream"])

        providerCmbBox = QComboBox()
        providerCmbBox.addItems(get_g4f_providers(including_auto=True))
        providerCmbBox.setCurrentText(self.__provider)
        providerCmbBox.currentTextChanged.connect(self.__providerChanged)

        # TODO LANGUAGE
        # TODO NEEDS ADDITIONAL DESCRIPTION
        g4f_use_chat_historyChkBox = QCheckBox("Use chat history")
        g4f_use_chat_historyChkBox.setChecked(
            CONFIG_MANAGER.get_general_property("g4f_use_chat_history")
        )
        g4f_use_chat_historyChkBox.toggled.connect(self.__saveChatHistory)

        lay = QFormLayout()
        lay.addRow(manualBrowser)
        lay.addRow(getSeparator("horizontal"))
        lay.addRow("Model", self.__modelCmbBox)
        lay.addRow("Provider", providerCmbBox)
        lay.addRow(streamChkBox)
        lay.addRow(g4f_use_chat_historyChkBox)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

    def __modelChanged(self, v):
        self.__model = v
        CONFIG_MANAGER.set_general_property("g4f_model", v)

    def __streamChecked(self, f):
        self.__stream = f
        CONFIG_MANAGER.set_general_property("stream", f)

    def __providerChanged(self, v):
        self.__modelCmbBox.clear()
        CONFIG_MANAGER.set_general_property("provider", v)
        if v == G4F_PROVIDER_DEFAULT:
            self.__modelCmbBox.addItems(get_g4f_models())
        else:
            self.__modelCmbBox.addItems(get_g4f_models_by_provider(v))

    def __saveChatHistory(self, f):
        CONFIG_MANAGER.set_general_property("g4f_use_chat_history", f)
