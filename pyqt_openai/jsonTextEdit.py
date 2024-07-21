import json
import sys
import re

from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from qtpy.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QPushButton, QMessageBox

from pyqt_openai.constants import FONT_FAMILY_FOR_SOURCE, INDENT_SIZE, DEFAULT_FONT_SIZE
from pyqt_openai.util.script import get_font


class JSONEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        font = get_font()
        font_size = font.get('font_size', DEFAULT_FONT_SIZE)
        font = QFont(FONT_FAMILY_FOR_SOURCE, font_size)

        self.setFont(font)
        self.setPlaceholderText("Enter JSON data here...")
        self.textChanged.connect(self.on_text_changed)
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineColor(QColor('red'))
        self.error_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor('blue'))
        self.check_json_timer = QTimer()
        self.check_json_timer.setSingleShot(True)
        self.check_json_timer.timeout.connect(self.validate_json)

    def on_text_changed(self):
        self.check_json_timer.start(500)  # Validate after 500ms

    def validate_json(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())  # Initialize format

        try:
            json_data = self.toPlainText()
            parsed_data = json.loads(json_data)
            self.highlight_keys(parsed_data)
        except json.JSONDecodeError as e:
            error_pos = e.pos
            cursor.setPosition(error_pos)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)
            cursor.setCharFormat(self.error_format)

    def highlight_keys(self, parsed_data):
        cursor = self.textCursor()
        self.setUpdatesEnabled(False)
        cursor.beginEditBlock()
        for match in self.find_iter(r'\"(.*?)\":'):
            cursor.setPosition(match[0])
            cursor.setPosition(match[1], QTextCursor.KeepAnchor)
            cursor.setCharFormat(self.key_format)
        cursor.endEditBlock()
        self.setUpdatesEnabled(True)

    def find_iter(self, pattern):
        regex = re.compile(pattern)
        for match in regex.finditer(self.toPlainText()):
            yield match.span()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_BraceLeft:
            super().keyPressEvent(event)
            self.insertPlainText('}')
            self.moveCursor(QTextCursor.PreviousCharacter)
        elif event.key() == Qt.Key.Key_QuoteDbl:
            super().keyPressEvent(event)
            self.insertPlainText('"')
            self.moveCursor(QTextCursor.PreviousCharacter)
        elif event.key() == Qt.Key.Key_BracketLeft:
            super().keyPressEvent(event)
            self.insertPlainText(']')
            self.moveCursor(QTextCursor.PreviousCharacter)
        elif event.key() == Qt.Key.Key_Tab and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            cursor = self.textCursor()
            if cursor.hasSelection():
                self.indent_selected_text()
            else:
                self.insertPlainText(' ' * INDENT_SIZE)
        elif event.key() == Qt.Key.Key_Tab and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            cursor = self.textCursor()
            if cursor.hasSelection():
                self.dedent_selected_text()
            else:
                self.dedent_text()
        else:
            super().keyPressEvent(event)

    def indent_selected_text(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.beginEditBlock()

        while cursor.position() < end:
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText(' ' * INDENT_SIZE)
            cursor.movePosition(QTextCursor.Down)

        cursor.endEditBlock()

    def dedent_selected_text(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.beginEditBlock()

        while cursor.position() < end:
            cursor.movePosition(QTextCursor.StartOfLine)
            line_text = cursor.block().text()
            if line_text.startswith(' ' * INDENT_SIZE):
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, INDENT_SIZE)
                for _ in range(INDENT_SIZE):
                    cursor.deleteChar()
            cursor.movePosition(QTextCursor.Down)

        cursor.endEditBlock()

    def dedent_text(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        line_text = cursor.block().text()
        if line_text.startswith(' ' * INDENT_SIZE):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, INDENT_SIZE)
            for _ in range(INDENT_SIZE):
                cursor.deleteChar()

    def format_json(self):
        try:
            json_data = self.toPlainText()
            parsed = json.loads(json_data)
            formatted = json.dumps(parsed, indent=INDENT_SIZE, sort_keys=True)
            self.setPlainText(formatted)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Invalid JSON", f"Error: {str(e)}")
#
# # Usage
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.init_ui()
#
#     def init_ui(self):
#         self.editor = JSONEditor()
#
#         self.format_button = QPushButton("Format JSON")
#         self.format_button.clicked.connect(self.format_json)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.editor)
#         layout.addWidget(self.format_button)
#
#         self.setLayout(layout)
#         self.setWindowTitle("JSON Editor")
#
#     def format_json(self):
#         return self.editor.format_json()
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
