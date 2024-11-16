from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from pyqt_openai.widgets.checkBoxListWidget import CheckBoxListWidget


class SupportedFileFormatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.__listWidget = CheckBoxListWidget()
        self.__listWidget.checkedSignal.connect(self.__sendCheckedSignal)

        ext_lst = ['.txt', '.docx', '.xlsx', '.md', '.pdf', '.html']

        self.__listWidget.addItems(ext_lst, checked=True)

        lay = QVBoxLayout()
        # TODO LANGUAGE
        lay.addWidget(QLabel('Supported File Formats'))
        lay.addWidget(self.__listWidget)
        self.setLayout(lay)

    def __sendCheckedSignal(self, r_idx, state):
        print(r_idx, state)