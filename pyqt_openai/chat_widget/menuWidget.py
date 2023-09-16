import os, sys

from qtpy.QtGui import QIcon

# Get the absolute path of the current script file
from pyqt_openai.chat_widget.chatBrowser import ChatBrowser

script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtCore import QPropertyAnimation, QAbstractAnimation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication

from chat_widget.findTextWidget import FindTextWidget


class MenuWidget(QWidget):
    def __init__(self, widget: ChatBrowser):
        super().__init__()
        self.__initUi(widget=widget)

    def __initUi(self, widget):
        findTextWidget = FindTextWidget(widget)

        self.__arrowBtn = QPushButton()
        self.__arrowBtn.toggled.connect(self.__toggled)

        lay = QHBoxLayout()
        lay.addWidget(findTextWidget)
        lay.addWidget(self.__arrowBtn)

        self.setLayout(lay)

        self.__foldUnfoldAnimation = QPropertyAnimation(self, b"height")
        self.__foldUnfoldAnimation.valueChanged.connect(self.setFixedHeight)
        self.__foldUnfoldAnimation.setStartValue(self.sizeHint().height())
        self.__foldUnfoldAnimation.setDuration(200)
        self.__foldUnfoldAnimation.setEndValue(0)

    def __toggled(self, f):
        if f:
            self.__fold()
            self.__arrowBtn.setIcon(QIcon('ico/unfold.svg'))
        else:
            self.__unfold()
            self.__arrowBtn.setIcon(QIcon('ico/fold.svg'))

    def __fold(self):
        self.__foldUnfoldAnimation.setDirection(QAbstractAnimation.Forward)
        self.__foldUnfoldAnimation.start()

    def __unfold(self):
        self.__foldUnfoldAnimation.setDirection(QAbstractAnimation.Backward)
        self.__foldUnfoldAnimation.start()



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MenuWidget()
    w.show()
    sys.exit(app.exec())