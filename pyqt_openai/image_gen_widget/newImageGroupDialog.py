from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QDialog, QComboBox, QFormLayout, QLineEdit, QFrame, QPushButton, QHBoxLayout, QWidget


class NewImageGroupDialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.__initUi(text)

    def __initUi(self, text):
        self.setWindowIcon(QIcon('ico/openai.svg'))
        self.setWindowTitle('New Image Group')
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self.__newName = QLineEdit(text)
        self.__newName.textChanged.connect(self.__setAccept)

        self.__imageModelCmbBox = QComboBox()
        self.__imageModelCmbBox.addItems(['DALL-E', 'Stable Diffusion'])

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__okBtn = QPushButton('OK')
        self.__okBtn.clicked.connect(self.accept)
        self.__okBtn.setEnabled(False)

        cancelBtn = QPushButton('Cancel')
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QFormLayout()
        lay.addRow('Choose the Model', self.__imageModelCmbBox)
        lay.addRow('Name of Image Group', self.__newName)
        lay.addRow(sep)
        lay.addRow(okCancelWidget)

        self.setLayout(lay)

    def __setAccept(self, text):
        self.__okBtn.setEnabled(text.strip() != '')

    def getModel(self):
        return self.__imageModelCmbBox.currentText()

    def getText(self):
        return self.__newName.text()
