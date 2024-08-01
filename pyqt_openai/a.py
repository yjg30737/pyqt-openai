from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QTextCursor

class CursorPositionExample(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the QTextEdit and QLabel to display cursor position
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(
            "This is the first line.\nThis is the second line.\nThis is the third line."
        )
        self.cursor_position_label = QLabel(self)

        # Connect the cursor position change signal
        self.text_edit.cursorPositionChanged.connect(self.update_cursor_position)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.cursor_position_label)
        self.setLayout(layout)

        # Initial update of cursor position
        self.update_cursor_position()

    def update_cursor_position(self):
        cursor = self.text_edit.textCursor()
        line_number = cursor.blockNumber() + 1  # Convert to 1-based index
        column_number = cursor.positionInBlock() + 1  # Convert to 1-based index

        # Update the QLabel with current cursor position
        self.cursor_position_label.setText(
            f"Line: {line_number}, Column: {column_number}"
        )

if __name__ == "__main__":
    app = QApplication([])
    window = CursorPositionExample()
    window.show()
    app.exec_()
