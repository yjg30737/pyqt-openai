from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import QGraphicsColorizeEffect, QWidget, QToolButton

from pyqt_openai.util.button_style_helper import ButtonStyleHelper


class ToolButton(QToolButton):
    def __init__(self, base_widget: QWidget = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
