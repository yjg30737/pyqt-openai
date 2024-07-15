from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QFormLayout, QLabel, QFrame, QPushButton

from pyqt_openai.models import ChatMessageContainer


class MessageResultDialog(QDialog):
    def __init__(self, result_info: ChatMessageContainer):
        super(MessageResultDialog, self).__init__()
        self.__initVal(result_info)
        self.__initUi()

    def __initVal(self, result_info):
        self.__result_info = result_info

    def __initUi(self):
        self.setWindowTitle('Message Result')
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        lbls = []
        for k, v in self.__result_info.get_items(excludes=['content']):
            if k == 'favorite':
                lbls.append(QLabel(f'{k}: {"Yes" if v else "No"}'))
            else:
                lbls.append(QLabel(f'{k}: {v}'))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        okBtn = QPushButton('OK')
        okBtn.clicked.connect(self.accept)

        lay = QFormLayout()
        for lbl in lbls:
            lay.addWidget(lbl)
        lay.addWidget(sep)
        lay.addWidget(okBtn)

        self.setLayout(lay)