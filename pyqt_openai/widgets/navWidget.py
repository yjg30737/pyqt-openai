from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class NavBar(QWidget):
    item_clicked = Signal(int)  # Signal to emit the index when an item is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__buttons = []  # List to store button references

    def __initUi(self):
        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def add(self, name):
        """Add a new navigation item."""
        button = QPushButton(name)
        button_style = """
                    QPushButton {
                        border: none;
                        background-color: transparent;
                        font-family: "Arial";
                        font-size: 16px;
                        padding: 10px 15px;
                    }
                    QPushButton:hover {
                        color: #007BFF;  /* Highlight color */
                    }
                """
        button.setStyleSheet(button_style)
        index = len(self.__buttons)
        button.clicked.connect(lambda: self.item_clicked.emit(index))
        self.layout().addWidget(button)
        self.__buttons.append(button)

    def set_active_button(self, active_index):
        """Set the active button as bold."""
        for index, button in enumerate(self.__buttons):
            font = button.font()
            font.setBold(index == active_index)
            button.setFont(font)