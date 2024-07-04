from qtpy.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QFrame, QPushButton, QHBoxLayout, QWidget
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon

from pyqt_openai.res.language_dict import LangClass


class InputDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.__initUi(title, text)

    def __initUi(self, title, text):
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__newName = QLineEdit(text)
        self.__newName.textChanged.connect(self.__setAccept)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS['OK'])
        self.__okBtn.clicked.connect(self.accept)

        cancelBtn = QPushButton(LangClass.TRANSLATIONS['Cancel'])
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__newName)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

    def getText(self):
        return self.__newName.text()

    def __setAccept(self, text):
        self.__okBtn.setEnabled(text.strip() != '')