from qtpy.QtWidgets import QDialog, QFormLayout, QApplication, QLabel, QFrame, QPushButton
from qtpy.QtCore import Qt


class ConvUnitResultDialog(QDialog):
    def __init__(self, result_info):
        super(ConvUnitResultDialog, self).__init__()
        self.__initVal(result_info)
        self.__initUi()

    def __initVal(self, result_info):
        self.__result_info = result_info

    def __initUi(self):
        self.setWindowTitle('Conversation Result')
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        model_nameLbl = QLabel('model_nameLbl')
        finish_reasonLbl = QLabel('finish_reasonLbl')
        prompt_tokensLbl = QLabel('prompt_tokensLbl')
        completion_tokensLbl = QLabel('completion_tokensLbl')
        total_tokensLbl = QLabel('total_tokensLbl')

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        okBtn = QPushButton('OK')
        okBtn.clicked.connect(self.accept)

        lay = QFormLayout()
        lay.addWidget(model_nameLbl)
        lay.addWidget(finish_reasonLbl)
        lay.addWidget(prompt_tokensLbl)
        lay.addWidget(completion_tokensLbl)
        lay.addWidget(total_tokensLbl)
        lay.addWidget(sep)
        lay.addWidget(okBtn)

        self.setLayout(lay)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ConvUnitResultDialog()
    w.show()
    sys.exit(app.exec())