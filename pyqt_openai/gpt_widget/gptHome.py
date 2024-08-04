from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea


class GPTHome(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel('Welcome to GPT Page !', self)
        title.setFont(QFont('Arial', 32))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel('Chat with GPT, all day long!' + '\n'*2)

        description.setFont(QFont('Arial', 16))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)