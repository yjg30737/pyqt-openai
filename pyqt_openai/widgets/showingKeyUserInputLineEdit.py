# TODO WILL_BE_USED AFTER v1.1.0

# This works perfectly for showing the key combination in a QLineEdit widget.

from qtpy.QtCore import Qt
from qtpy.QtGui import QKeyEvent
from qtpy.QtWidgets import QLineEdit


class ShowingKeyUserInputLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shortcut = ""

    def keyPressEvent(self, event: QKeyEvent):
        modifiers = event.modifiers()
        key = event.key()

        key_text = self._get_key_text(key)
        if key_text:
            parts = []

            if modifiers & Qt.KeyboardModifier.ControlModifier:
                parts.append('Ctrl')
            if modifiers & Qt.KeyboardModifier.AltModifier:
                parts.append('Alt')
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                parts.append('Shift')
            if modifiers & Qt.KeyboardModifier.MetaModifier:
                parts.append('Meta')

            parts.append(key_text)
            self.shortcut = '+'.join(parts)
            self.setText(self.shortcut)

    def _get_key_text(self, key):
        special_keys = {
            Qt.Key.Key_Escape: 'Esc', Qt.Key.Key_Tab: 'Tab', Qt.Key.Key_Backtab: 'Backtab',
            Qt.Key.Key_Backspace: 'Backspace', Qt.Key.Key_Return: 'Return', Qt.Key.Key_Enter: 'Enter',
            Qt.Key.Key_Insert: 'Ins', Qt.Key.Key_Delete: 'Del', Qt.Key.Key_Pause: 'Pause', Qt.Key.Key_Print: 'Print',
            Qt.Key.Key_SysReq: 'SysReq', Qt.Key.Key_Clear: 'Clear', Qt.Key.Key_Home: 'Home', Qt.Key.Key_End: 'End',
            Qt.Key.Key_Left: 'Left', Qt.Key.Key_Up: 'Up', Qt.Key.Key_Right: 'Right', Qt.Key.Key_Down: 'Down',
            Qt.Key.Key_PageUp: 'PageUp', Qt.Key.Key_PageDown: 'PageDown', Qt.Key.Key_Space: 'Space',
            Qt.Key.Key_CapsLock: 'CapsLock', Qt.Key.Key_NumLock: 'NumLock', Qt.Key.Key_ScrollLock: 'ScrollLock',
            Qt.Key.Key_Menu: 'Menu', Qt.Key.Key_Help: 'Help'
        }

        if key in special_keys:
            return special_keys[key]
        elif 0x20 <= key <= 0x7E:  # Regular printable ASCII characters
            return chr(key)
        elif 0x100 <= key <= 0x10FFFF:  # Other valid Unicode characters
            try:
                return chr(key).upper()
            except ValueError:
                pass
        return None