from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtGui import QColor, QIcon
from qtpy.QtWidgets import QGraphicsColorizeEffect, QToolButton

from pyqt_openai.util.button_style_helper import ButtonStyleHelper

if TYPE_CHECKING:
    from qtpy.QtCore import QEvent, QObject
    from qtpy.QtWidgets import QWidget


class ToolButton(QToolButton):
    def __init__(
        self,
        base_widget: QWidget | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.style_helper: ButtonStyleHelper = ButtonStyleHelper(base_widget)
        self.setStyleSheet(self.style_helper.styleInit())
        self.installEventFilter(self)

    def setStyleAndIcon(
        self,
        icon: str,
    ):
        self.style_helper.__icon = icon
        self.setStyleSheet(self.style_helper.styleInit())
        self.setIcon(QIcon(icon))

    def eventFilter(
        self,
        obj: QObject,
        event: QEvent,
    ) -> bool:
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
