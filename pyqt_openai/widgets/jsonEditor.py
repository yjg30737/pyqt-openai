from __future__ import annotations

import json
import re

from typing import TYPE_CHECKING

from qtpy.QtCore import QTimer, Qt, Signal
from qtpy.QtGui import QColor, QTextCharFormat, QTextCursor
from qtpy.QtWidgets import QMessageBox, QTextEdit

from pyqt_openai import DEFAULT_SOURCE_ERROR_COLOR, DEFAULT_SOURCE_HIGHLIGHT_COLOR, INDENT_SIZE
from pyqt_openai.lang.translations import LangClass

if TYPE_CHECKING:
    from qtpy.QtGui import QKeyEvent
    from qtpy.QtWidgets import QFocusEvent, QWidget


class JSONEditor(QTextEdit):
    moveCursorToOtherPrompt = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        font = self.font()

        self.setFont(font)
        self.setPlaceholderText(LangClass.TRANSLATIONS["Enter JSON data here..."])
        self.textChanged.connect(self.on_text_changed)
        self.error_format: QTextCharFormat = QTextCharFormat()
        self.error_format.setUnderlineColor(QColor(DEFAULT_SOURCE_ERROR_COLOR))
        self.error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        self.key_format: QTextCharFormat = QTextCharFormat()
        self.key_format.setForeground(QColor(DEFAULT_SOURCE_HIGHLIGHT_COLOR))
        self.check_json_timer: QTimer = QTimer()
        self.check_json_timer.setSingleShot(True)
        self.check_json_timer.timeout.connect(self.validate_json)

    def on_text_changed(self):
        self.check_json_timer.start(500)  # Validate after 500ms

    def validate_json(self):
        cursor: QTextCursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())  # Initialize format

        try:
            json_data = self.toPlainText()
            parsed_data = json.loads(json_data)
            self.highlight_keys(parsed_data)
        except json.JSONDecodeError as e:
            error_pos = e.pos
            cursor.setPosition(error_pos)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
            cursor.setCharFormat(self.error_format)

    def highlight_keys(
        self,
        parsed_data: dict,
    ):
        cursor: QTextCursor = self.textCursor()
        self.setUpdatesEnabled(False)
        cursor.beginEditBlock()
        for match in self.find_iter(r"\"(.*?)\":"):
            cursor.setPosition(match[0])
            cursor.setPosition(match[1], QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(self.key_format)
        cursor.endEditBlock()
        self.setUpdatesEnabled(True)

    def find_iter(
        self,
        pattern: str,
    ):
        regex: re.Pattern = re.compile(pattern)
        for match in regex.finditer(self.toPlainText()):
            yield match.span()

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ):
        cursor: QTextCursor = self.textCursor()
        # If up and down keys are pressed and cursor is at the beginning or end of the text
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Up:
                self.moveCursorToOtherPrompt.emit("up")
                return None
            if event.key() == Qt.Key.Key_Down:
                self.moveCursorToOtherPrompt.emit("down")
                return None
            return super().keyPressEvent(event)

        if event.key() == Qt.Key.Key_BraceLeft:
            super().keyPressEvent(event)
            self.insertPlainText("\n\n")
            self.insertPlainText("}")
            cursor.movePosition(QTextCursor.MoveOperation.Up)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.insertText(" " * INDENT_SIZE)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key.Key_QuoteDbl:
            super().keyPressEvent(event)
            self.insertPlainText('"')
            cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
            self.setTextCursor(cursor)
        elif event.key() == Qt.Key.Key_BracketLeft:
            super().keyPressEvent(event)
            self.insertPlainText("]")
            cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
            self.setTextCursor(cursor)
        elif (
            event.key() == Qt.Key.Key_Tab
            and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            cursor = self.textCursor()
            if cursor.hasSelection():
                self.indent_selected_text()
            else:
                self.insertPlainText(" " * INDENT_SIZE)
        elif (
            event.key() == Qt.Key.Key_Tab
            and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            cursor = self.textCursor()
            if cursor.hasSelection():
                self.dedent_selected_text()
            else:
                self.dedent_text()
        else:
            super().keyPressEvent(event)

    def indent_selected_text(self):
        cursor: QTextCursor = self.textCursor()
        start: int = cursor.selectionStart()
        end: int = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.beginEditBlock()

        while cursor.position() < end:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.insertText(" " * INDENT_SIZE)
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        cursor.endEditBlock()

    def dedent_selected_text(self):
        cursor: QTextCursor = self.textCursor()
        start: int = cursor.selectionStart()
        end: int = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.beginEditBlock()

        while cursor.position() < end:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            line_text = cursor.block().text()
            if line_text.startswith(" " * INDENT_SIZE):
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    INDENT_SIZE,
                )
                for _ in range(INDENT_SIZE):
                    cursor.deleteChar()
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        cursor.endEditBlock()

    def dedent_text(self):
        cursor: QTextCursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        line_text: str = cursor.block().text()
        if line_text.startswith(" " * INDENT_SIZE):
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                INDENT_SIZE,
            )
            for _ in range(INDENT_SIZE):
                cursor.deleteChar()

    def format_json(self):
        try:
            json_data: str = self.toPlainText()
            parsed: dict = json.loads(json_data)
            formatted: str = json.dumps(parsed, indent=INDENT_SIZE, sort_keys=True)
            self.setPlainText(formatted)
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                None,  # pyright: ignore[reportArgumentType]
                "Invalid JSON",
                f"Error: {e!s}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.No,
            )

    def focusInEvent(self, event: QFocusEvent):
        self.setCursorWidth(1)
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        self.setCursorWidth(0)
        return super().focusInEvent(event)


# # Usage
# class AIWidget(QWidget):
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
#     window = AIWidget()
#     window.show()
#     sys.exit(app.exec_())
