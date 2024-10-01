from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QCheckBox, QHBoxLayout, QLabel

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.globals import get_chat_model
from pyqt_openai.lang.translations import LangClass


class UsingG4FPage(QWidget):
    onToggleLlama = Signal(bool)
    onToggleJSON = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__stream = CONFIG_MANAGER.get_general_property('stream')
        self.__model = CONFIG_MANAGER.get_general_property('model')

    def __initUi(self):
        modelCmbBox = QComboBox()
        modelCmbBox.addItems(get_chat_model(is_g4f=True))
        modelCmbBox.setCurrentText(self.__model)
        modelCmbBox.currentTextChanged.connect(self.__modelChanged)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Model']))
        lay.addWidget(modelCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        selectModelWidget = QWidget()
        selectModelWidget.setLayout(lay)

        streamChkBox = QCheckBox()
        streamChkBox.setChecked(self.__stream)
        streamChkBox.toggled.connect(self.__streamChecked)
        streamChkBox.setText(LangClass.TRANSLATIONS['Stream'])

        lay = QVBoxLayout()
        lay.addWidget(selectModelWidget)
        lay.addWidget(streamChkBox)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(lay)

    def __modelChanged(self, v):
        self.__model = v
        CONFIG_MANAGER.set_general_property('model', v)

    def __streamChecked(self, f):
        self.__stream = f
        CONFIG_MANAGER.set_general_property('stream', f)