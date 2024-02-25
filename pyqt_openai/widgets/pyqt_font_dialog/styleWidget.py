from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QCheckBox, QGridLayout


class StyleWidget(QWidget):
    boldChecked = pyqtSignal(int)
    italicChecked = pyqtSignal(int)

    def __init__(self, font: QFont = QFont('Arial', 10)):
        super().__init__()
        self.__initUi(font=font)

    def __initUi(self, font: QFont):
        groupBox = QGroupBox()
        groupBox.setTitle('Style')

        self.__boldChkBox = QCheckBox('Bold')
        self.__italicChkBox = QCheckBox('Italic')

        self.__boldChkBox.stateChanged.connect(self.boldChecked)
        self.__italicChkBox.stateChanged.connect(self.italicChecked)

        self.__initCurrentStyle(font=font)

        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self.__boldChkBox)
        lay.addWidget(self.__italicChkBox)

        groupBox.setLayout(lay)

        lay = QGridLayout()
        lay.addWidget(groupBox)

        self.setLayout(lay)

    def __initCurrentStyle(self, font: QFont):
        self.__boldChkBox.setChecked(font.bold())
        self.__italicChkBox.setChecked(font.italic())

    def isBold(self):
        return self.__boldChkBox.isChecked()

    def isItalic(self):
        return self.__italicChkBox.isChecked()
