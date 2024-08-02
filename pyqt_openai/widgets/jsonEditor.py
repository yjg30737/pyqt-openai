import json
import re

from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtGui import QTextCursor, QTextCharFormat, QColor
from qtpy.QtWidgets import QTextEdit, QMessageBox

from pyqt_openai import INDENT_SIZE, DEFAULT_SOURCE_HIGHLIGHT_COLOR, DEFAULT_SOURCE_ERROR_COLOR
from pyqt_openai.lang.translations import LangClass


class JSONEditor(QTextEdit):
    moveCursorToOtherPrompt = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        font = self.font()

        self.setFont(font)
        self.setPlaceholderText(LangClass.TRANSLATIONS["Enter JSON data here..."])
        self.textChanged.connect(self.on_text_changed)
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineColor(QColor(DEFAULT_SOURCE_ERROR_COLOR))
        self.error_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor(DEFAULT_SOURCE_HIGHLIGHT_COLOR))
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
        cursor = self.textCursor()
        # If up and down keys are pressed and cursor is at the beginning or end of the text
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Up:
                self.moveCursorToOtherPrompt.emit('up')
                return
            elif event.key() == Qt.Key.Key_Down:
                self.moveCursorToOtherPrompt.emit('down')
                return
            else:
                return super().keyPressEvent(event)

        if event.key() == Qt.Key.Key_BraceLeft:
            super().keyPressEvent(event)
            self.insertPlainText('\n\n')
            self.insertPlainText('}')
            cursor.movePosition(QTextCursor.Up)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText(' ' * INDENT_SIZE)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key.Key_QuoteDbl:
            super().keyPressEvent(event)
            self.insertPlainText('"')
            cursor.movePosition(QTextCursor.PreviousCharacter)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key.Key_BracketLeft:
            super().keyPressEvent(event)
            self.insertPlainText(']')
            cursor.movePosition(QTextCursor.PreviousCharacter)
            self.setTextCursor(cursor)
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

    def focusInEvent(self, event):
        self.setCursorWidth(1)
        return super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setCursorWidth(0)
        return super().focusInEvent(event)

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
