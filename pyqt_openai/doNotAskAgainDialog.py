from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QApplication, QFrame, QHBoxLayout, QWidget, \
QCheckBox, QSpacerItem, QSizePolicy


class DoNotAskAgainDialog(QDialog):
    doNotAskAgainChanged = Signal(bool)

    def __init__(self, do_not_ask_again: bool = False,
                 do_not_ask_again_message: str = "Would you like to exit the application? If you won\'t, it will be running in the background.",
                do_not_ask_again_checkbox_message: str = 'Do not ask again'):
        super().__init__()
        self.__initVal(do_not_ask_again, do_not_ask_again_message, do_not_ask_again_checkbox_message)
        self.__initUi()

    def __initVal(self, do_not_ask_again, do_not_ask_again_message, do_not_ask_again_checkbox_message):
        self.__is_cancel = False
        self.__do_not_ask_again = do_not_ask_again
        self.__do_not_ask_again_message = do_not_ask_again_message
        self.__do_not_ask_again_checkbox_message = do_not_ask_again_checkbox_message

    def __initUi(self):
        self.setWindowTitle("Exit")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.label = QLabel(self.__do_not_ask_again_message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.yesButton = QPushButton("Yes")
        self.yesButton.clicked.connect(self.accept)

        self.noButton = QPushButton("No")
        self.noButton.clicked.connect(self.reject)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.__cancel)

        self.doNotAskAgainCheckBox = QCheckBox(self.__do_not_ask_again_checkbox_message)
        self.doNotAskAgainCheckBox.setChecked(self.__do_not_ask_again)
        self.doNotAskAgainCheckBox.stateChanged.connect(self.__onCheckBoxStateChanged)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        lay = QHBoxLayout()
        lay.addWidget(self.doNotAskAgainCheckBox)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.yesButton)
        lay.addWidget(self.noButton)
        lay.addWidget(self.cancelButton)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0,0,0,0)
        btnWidget = QWidget()
        btnWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.label)
        lay.addWidget(sep)
        lay.addWidget(btnWidget)

        self.setLayout(lay)

    def __cancel(self):
        self.__is_cancel = True
        self.reject()

    def __onCheckBoxStateChanged(self, state):
        self.__do_not_ask_again = state == 2
        self.doNotAskAgainChanged.emit(self.__do_not_ask_again)

    def isCancel(self):
        return self.__is_cancel


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = DoNotAskAgainDialog()
    w.show()
    sys.exit(app.exec())