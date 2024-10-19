from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QDoubleSpinBox,
    QSpinBox,
    QFormLayout,
    QSizePolicy,
    QComboBox,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QCheckBox,
    QPushButton,
    QScrollArea,
    QGroupBox,
    QHBoxLayout,
    QTextBrowser,
)

from pyqt_openai import (
    DEFAULT_SHORTCUT_JSON_MODE,
    OPENAI_TEMPERATURE_RANGE,
    OPENAI_TEMPERATURE_STEP,
    MAX_TOKENS_RANGE,
    TOP_P_RANGE,
    TOP_P_STEP,
    FREQUENCY_PENALTY_RANGE,
    PRESENCE_PENALTY_STEP,
    PRESENCE_PENALTY_RANGE,
    FREQUENCY_PENALTY_STEP,
    LLAMAINDEX_URL,
    O1_MODELS,
    SMALL_LABEL_PARAM,
)
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import (
    getSeparator,
    get_chat_model,
    get_openai_chat_model,
    init_llama,
)
from pyqt_openai.widgets.linkLabel import LinkLabel
from pyqt_openai.widgets.modernButton import ModernButton


class UsingAPIPage(QWidget):
    onToggleLlama = Signal(bool)
    onToggleJSON = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__stream = CONFIG_MANAGER.get_general_property("stream")
        self.__model = CONFIG_MANAGER.get_general_property("model")
        self.__system = CONFIG_MANAGER.get_general_property("system")
        self.__temperature = CONFIG_MANAGER.get_general_property("temperature")
        self.__max_tokens = CONFIG_MANAGER.get_general_property("max_tokens")
        self.__top_p = CONFIG_MANAGER.get_general_property("top_p")
        self.__frequency_penalty = CONFIG_MANAGER.get_general_property(
            "frequency_penalty"
        )
        self.__presence_penalty = CONFIG_MANAGER.get_general_property(
            "presence_penalty"
        )
        self.__json_object = CONFIG_MANAGER.get_general_property("json_object")

        self.__use_max_tokens = CONFIG_MANAGER.get_general_property("use_max_tokens")
        self.__use_llama_index = CONFIG_MANAGER.get_general_property("use_llama_index")

    def __initUi(self):
        manualBrowser = QTextBrowser()
        manualBrowser.setOpenExternalLinks(True)
        manualBrowser.setOpenLinks(True)

        # TODO LANGUAGE
        manualBrowser.setHtml(
            """
        <h2>Using API</h2>
        <h3>Description</h3>
        <p>- Fast responses.</p>
        <p>- Stable response server.</p>
        <p>- Ability to save your AI usage history and statistics.</p>
        <p>- Option to add custom LLMs you have created.</p>
        <p>- Ability to save conversation history on the server.</p>
        <p>- JSON response functionality available (limited to specific LLMs).</p>
        <p>- LlamaIndex can be used.</p>
        <p>- Various hyperparameters can be assigned.</p>
        """
        )

        manualBrowser.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )

        systemlbl = QLabel(LangClass.TRANSLATIONS["System"])
        systemlbl.setToolTip(
            LangClass.TRANSLATIONS[
                "Basically system means instructions or rules that the model should follow."
            ]
            + "\n"
            + LangClass.TRANSLATIONS["You can write your own system instructions here."]
        )

        self.__systemTextEdit = QTextEdit()
        self.__systemTextEdit.setText(self.__system)
        self.__systemTextEdit.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred
        )
        saveSystemBtn = QPushButton(LangClass.TRANSLATIONS["Save System"])
        saveSystemBtn.clicked.connect(self.__saveSystem)

        modelCmbBox = QComboBox()
        modelCmbBox.addItems(get_chat_model())
        modelCmbBox.setCurrentText(self.__model)
        modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Model"]))
        lay.addWidget(modelCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        setApiBtn = ModernButton()
        # TODO LANGUAGE
        setApiBtn.setText("Set API Key")

        selectModelWidget = QWidget()
        selectModelWidget.setLayout(lay)

        self.__warningLbl = QLabel()
        self.__warningLbl.setStyleSheet("color: orange;")
        self.__warningLbl.setVisible(False)
        self.__warningLbl.setWordWrap(True)
        self.__warningLbl.setFont(QFont(SMALL_LABEL_PARAM))

        advancedSettingsScrollArea = QScrollArea()

        self.__temperatureSpinBox = QDoubleSpinBox()
        self.__temperatureSpinBox.setRange(*OPENAI_TEMPERATURE_RANGE)
        self.__temperatureSpinBox.setAccelerated(True)
        self.__temperatureSpinBox.setSingleStep(OPENAI_TEMPERATURE_STEP)
        self.__temperatureSpinBox.setValue(self.__temperature)
        self.__temperatureSpinBox.valueChanged.connect(self.__valueChanged)
        self.__temperatureSpinBox.setToolTip(
            LangClass.TRANSLATIONS[
                "To control the randomness of responses, you adjust the temperature parameter."
            ]
            + "\n"
            + LangClass.TRANSLATIONS[
                "A lower value results in less random completions."
            ]
        )

        self.__maxTokensSpinBox = QSpinBox()
        self.__maxTokensSpinBox.setRange(*MAX_TOKENS_RANGE)
        self.__maxTokensSpinBox.setAccelerated(True)
        self.__maxTokensSpinBox.setValue(self.__max_tokens)
        self.__maxTokensSpinBox.valueChanged.connect(self.__valueChanged)
        self.__maxTokensSpinBox.setToolTip(
            LangClass.TRANSLATIONS[
                "To set a limit on the number of tokens to generate, you use the max tokens parameter."
            ]
            + "\n"
            + LangClass.TRANSLATIONS[
                "The model will stop generating tokens once it reaches the limit."
            ]
        )

        self.__toppSpinBox = QDoubleSpinBox()
        self.__toppSpinBox.setRange(*TOP_P_RANGE)
        self.__toppSpinBox.setAccelerated(True)
        self.__toppSpinBox.setSingleStep(TOP_P_STEP)
        self.__toppSpinBox.setValue(self.__top_p)
        self.__toppSpinBox.valueChanged.connect(self.__valueChanged)
        self.__toppSpinBox.setToolTip(
            LangClass.TRANSLATIONS[
                "To set a threshold for nucleus sampling, you use the top p parameter."
            ]
            + "\n"
            + LangClass.TRANSLATIONS[
                "The model will stop generating tokens once the cumulative probability of the generated tokens exceeds the threshold."
            ]
        )

        self.__frequencyPenaltySpinBox = QDoubleSpinBox()
        self.__frequencyPenaltySpinBox.setRange(*FREQUENCY_PENALTY_RANGE)
        self.__frequencyPenaltySpinBox.setAccelerated(True)
        self.__frequencyPenaltySpinBox.setSingleStep(FREQUENCY_PENALTY_STEP)
        self.__frequencyPenaltySpinBox.setValue(self.__frequency_penalty)
        self.__frequencyPenaltySpinBox.valueChanged.connect(self.__valueChanged)
        self.__frequencyPenaltySpinBox.setToolTip(
            LangClass.TRANSLATIONS[
                "To penalize the model from repeating the same tokens, you use the frequency penalty parameter."
            ]
            + "\n"
            + LangClass.TRANSLATIONS[
                "The model will be less likely to generate tokens that have already been generated."
            ]
        )

        self.__presencePenaltySpinBox = QDoubleSpinBox()
        self.__presencePenaltySpinBox.setRange(*PRESENCE_PENALTY_RANGE)
        self.__presencePenaltySpinBox.setAccelerated(True)
        self.__presencePenaltySpinBox.setSingleStep(PRESENCE_PENALTY_STEP)
        self.__presencePenaltySpinBox.setValue(self.__presence_penalty)
        self.__presencePenaltySpinBox.valueChanged.connect(self.__valueChanged)
        self.__presencePenaltySpinBox.setToolTip(
            LangClass.TRANSLATIONS[
                "To penalize the model from generating tokens that are not present in the input, you use the presence penalty parameter."
            ]
            + "\n"
            + LangClass.TRANSLATIONS[
                "The model will be less likely to generate tokens that are not present in the input."
            ]
        )

        useMaxTokenChkBox = QCheckBox()
        useMaxTokenChkBox.toggled.connect(self.__useMaxChecked)
        useMaxTokenChkBox.setChecked(self.__use_max_tokens)
        useMaxTokenChkBox.setText(LangClass.TRANSLATIONS["Use Max Tokens"])

        self.__maxTokensSpinBox.setEnabled(self.__use_max_tokens)

        lay = QFormLayout()

        lay.addRow(useMaxTokenChkBox)
        lay.addRow("Temperature", self.__temperatureSpinBox)
        lay.addRow("Max Tokens", self.__maxTokensSpinBox)
        lay.addRow("Top p", self.__toppSpinBox)
        lay.addRow("Frequency Penalty", self.__frequencyPenaltySpinBox)
        lay.addRow("Presence Penalty", self.__presencePenaltySpinBox)

        paramWidget = QWidget()
        paramWidget.setLayout(lay)

        advancedSettingsScrollArea.setWidgetResizable(True)
        advancedSettingsScrollArea.setWidget(paramWidget)

        lay = QVBoxLayout()
        lay.addWidget(advancedSettingsScrollArea)

        advancedSettingsGrpBox = QGroupBox(LangClass.TRANSLATIONS["Advanced Settings"])
        advancedSettingsGrpBox.setLayout(lay)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText(LangClass.TRANSLATIONS["Stream"])

        self.__jsonChkBox = QCheckBox()
        self.__jsonChkBox.setChecked(self.__json_object)
        self.__jsonChkBox.toggled.connect(self.__jsonObjectChecked)

        self.__jsonChkBox.setText(LangClass.TRANSLATIONS["Enable JSON mode"])
        self.__jsonChkBox.setShortcut(DEFAULT_SHORTCUT_JSON_MODE)
        self.__jsonChkBox.setToolTip(
            LangClass.TRANSLATIONS[
                "When enabled, you can send a JSON object to the API and the response will be in JSON format. Otherwise, it will be in plain text."
            ]
        )

        # TODO LANGUAGE
        llamaManualLbl = LinkLabel()
        llamaManualLbl.setText(LangClass.TRANSLATIONS["What is LlamaIndex?"])
        llamaManualLbl.setUrl(LLAMAINDEX_URL)

        self.__llamaChkBox = QCheckBox()
        self.__llamaChkBox.setChecked(self.__use_llama_index)
        self.__llamaChkBox.toggled.connect(self.__use_llama_indexChecked)
        self.__llamaChkBox.setText(LangClass.TRANSLATIONS["Use LlamaIndex"])

        lay = QVBoxLayout()
        lay.addWidget(manualBrowser)
        lay.addWidget(getSeparator("horizontal"))
        lay.addWidget(systemlbl)
        lay.addWidget(self.__systemTextEdit)
        lay.addWidget(saveSystemBtn)
        lay.addWidget(getSeparator("horizontal"))
        lay.addWidget(setApiBtn)
        lay.addWidget(selectModelWidget)
        lay.addWidget(self.__warningLbl)
        lay.addWidget(streamChkBox)
        lay.addWidget(self.__jsonChkBox)
        lay.addWidget(self.__llamaChkBox)
        lay.addWidget(llamaManualLbl)
        lay.addWidget(getSeparator("horizontal"))
        lay.addWidget(advancedSettingsGrpBox)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

    def __saveSystem(self):
        self.__system = self.__systemTextEdit.toPlainText()
        CONFIG_MANAGER.set_general_property("system", self.__system)

    def __modelChanged(self, v):
        self.__model = v
        CONFIG_MANAGER.set_general_property("model", v)
        # TODO LANGUAGE
        if self.__model in O1_MODELS:
            self.__warningLbl.setText(
                "Note: The selected model is only available at Tier 3 or higher."
            )
            self.__warningLbl.setVisible(True)
        else:
            self.__warningLbl.setText(
                "Note: The selected model does not support LlamaIndex, JSON mode."
            )
            f = v in get_openai_chat_model()
            self.__jsonChkBox.setEnabled(f)
            self.__llamaChkBox.setEnabled(f)
            self.__warningLbl.setVisible(not f)

    def __streamChecked(self, f):
        self.__stream = f
        CONFIG_MANAGER.set_general_property("stream", f)

    def __jsonObjectChecked(self, f):
        self.__json_object = f
        CONFIG_MANAGER.set_general_property("json_object", f)
        self.onToggleJSON.emit(f)

    def __use_llama_indexChecked(self, f):
        self.__use_llama_index = f
        CONFIG_MANAGER.set_general_property("use_llama_index", f)
        if f:
            # Set llama index directory if it exists
            init_llama()
        self.onToggleLlama.emit(f)

    def __useMaxChecked(self, f):
        self.__use_max_tokens = f
        CONFIG_MANAGER.set_general_property("use_max_tokens", f)
        self.__maxTokensSpinBox.setEnabled(f)

    def __valueChanged(self, v):
        sender = self.sender()
        if sender == self.__temperatureSpinBox:
            self.__temperature = v
            CONFIG_MANAGER.set_general_property("temperature", v)
        elif sender == self.__maxTokensSpinBox:
            self.__max_tokens = v
            CONFIG_MANAGER.set_general_property("max_tokens", v)
        elif sender == self.__toppSpinBox:
            self.__top_p = v
            CONFIG_MANAGER.set_general_property("top_p", v)
        elif sender == self.__frequencyPenaltySpinBox:
            self.__frequency_penalty = v
            CONFIG_MANAGER.set_general_property("frequency_penalty", v)
        elif sender == self.__presencePenaltySpinBox:
            self.__presence_penalty = v
            CONFIG_MANAGER.set_general_property("presence_penalty", v)
