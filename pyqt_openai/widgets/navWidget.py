from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from qtpy.QtGui import QFont


class NavBar(QWidget):
    itemClicked = Signal(int)  # Signal to emit the index when an item is clicked

    def __init__(
        self,
        parent: QWidget | None = None,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    ):
        super().__init__(parent)
        self.__initVal()
        self.__initUi(orientation)

    def __initVal(self):
        self.__buttons: list[QPushButton] = []  # List to store button references

    def __initUi(self, orientation: Qt.Orientation):
        if orientation == Qt.Orientation.Horizontal:
            lay = QHBoxLayout()
            lay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            lay = QVBoxLayout()
            lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def add(
        self,
        name: str,
    ):
        """Add a new navigation item."""
        button: QPushButton = QPushButton(name)
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
        button.clicked.connect(lambda: self.itemClicked.emit(index))
        self.layout().addWidget(button)
        self.__buttons.append(button)

    def setActiveButton(
        self,
        active_index: int,
    ):
        """Set the active button as bold."""
        for index, button in enumerate(self.__buttons):
            font: QFont = button.font()
            font.setBold(index == active_index)
            button.setFont(font)
