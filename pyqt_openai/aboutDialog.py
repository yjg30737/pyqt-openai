from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QLabel


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('About')
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self.__okBtn = QPushButton('OK')
        self.__okBtn.clicked.connect(self.accept)

        p = QPixmap('pyqtopenai.png')
        logoLbl = QLabel()
        logoLbl.setPixmap(p)

        expWidget = QLabel()
        expWidget.setText('''
        <h1>pyqt-openai</h1>
        <p>Version below 1</p>
        <p>Powered by PyQt</p>
        ''')
        expWidget.setAlignment(Qt.AlignTop)

        lay = QHBoxLayout()
        lay.addWidget(logoLbl)
        lay.addWidget(expWidget)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        cancelBtn = QPushButton('Cancel')
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

