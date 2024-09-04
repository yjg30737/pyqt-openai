import os.path, posixpath

from PySide6.QtGui import QColor, QPalette, qGray, QIcon
from PySide6.QtWidgets import QGraphicsColorizeEffect, QWidget, QApplication, QPushButton

from pyqt_openai import SRC_DIR, DEFAULT_BUTTON_HOVER_COLOR, DEFAULT_BUTTON_PRESSED_COLOR, DEFAULT_BUTTON_CHECKED_COLOR
from pyqt_openai.util.button_style_helper import ButtonStyleHelper


class Button(QPushButton):
    def __init__(self, base_widget: QWidget = None, parent=None):
        super().__init__(parent)
        self.style_helper = ButtonStyleHelper(base_widget)
        self.setStyleSheet(self.style_helper.styleInit())
        self.installEventFilter(self)

    def setStyleAndIcon(self, icon: str):
        self.style_helper.__icon = icon
        self.setStyleSheet(self.style_helper.styleInit())
        self.setIcon(QIcon(icon))

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == 98:  # Event type for EnableChange
                effect = QGraphicsColorizeEffect()
                effect.setColor(QColor(255, 255, 255))
                if self.isEnabled():
                    effect.setStrength(0)
                else:
                    effect.setStrength(1)
                    effect.setColor(QColor(150, 150, 150))
                self.setGraphicsEffect(effect)
        return super().eventFilter(obj, event)