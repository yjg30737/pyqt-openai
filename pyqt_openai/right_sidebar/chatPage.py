from PyQt5.QtWidgets import QWidget, QComboBox, QTextEdit, QLabel, QVBoxLayout, QApplication, QCheckBox


class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        systemlbl = QLabel('System')
        systemTextEdit = QTextEdit()
        systemTextEdit.setText('You are a helpful assistant.')
        cmbBox = QComboBox()

        streamChkBox = QCheckBox('Stream')
        finishReasonChkBox = QCheckBox('Show Finish Reason')

        lay = QVBoxLayout()
        lay.addWidget(systemlbl)
        lay.addWidget(systemTextEdit)
        lay.addWidget(cmbBox)
        lay.addWidget(streamChkBox)
        lay.addWidget(finishReasonChkBox)

        self.setLayout(lay)


if __name__ == '__main__':
    app = QApplication([])
    window = ChatPage()
    window.show()
    app.exec_()
