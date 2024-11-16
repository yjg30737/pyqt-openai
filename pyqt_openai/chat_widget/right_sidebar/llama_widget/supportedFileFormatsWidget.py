from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from pyqt_openai import LLAMA_INDEX_DEFAULT_ALL_SUPPORTED_FORMATS_LIST
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget


class SupportedFileFormatsWidget(QWidget):
    checkedSignal = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.__listWidget = CheckBoxListWidget()
        self.__listWidget.checkedSignal.connect(self.__sendCheckedSignal)

        all_supported_format_lst = LLAMA_INDEX_DEFAULT_ALL_SUPPORTED_FORMATS_LIST
        self.__listWidget.addItems(all_supported_format_lst)

        current_supported_format_lst = CONFIG_MANAGER.get_general_property("llama_index_supported_formats")
        for i in range(self.__listWidget.count()):
            supported_format = self.__listWidget.item(i).text()
            if supported_format in current_supported_format_lst:
                self.__listWidget.item(i).setCheckState(Qt.CheckState.Checked)

        lay = QVBoxLayout()
        # TODO LANGUAGE
        lay.addWidget(QLabel('Supported File Formats'))
        lay.addWidget(self.__listWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def __sendCheckedSignal(self, r_idx, state):
        self.checkedSignal.emit(self.__listWidget.getCheckedItemsText())