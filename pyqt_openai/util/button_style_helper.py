from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtGui import QColor, QPalette, qGray
from qtpy.QtWidgets import (
    QApplication,
)

from pyqt_openai import (
    DEFAULT_BUTTON_CHECKED_COLOR,
    DEFAULT_BUTTON_HOVER_COLOR,
    DEFAULT_BUTTON_PRESSED_COLOR,
)

if TYPE_CHECKING:
    from qtpy.QtWidgets import (
        QWidget,
    )


class ButtonStyleHelper:
    def __init__(self, base_widget: QWidget = None):
        self.__baseWidget = base_widget
        self.__initVal()

    def __initVal(self):
        # to set size accordance with scale
        sc = QApplication.screens()[0]
        sc.logicalDotsPerInchChanged.connect(self.__scaleChanged)
        self.__size = sc.logicalDotsPerInch() // 4
        self.__padding = self.__border_radius = self.__size // 10
        self.__background_color = "transparent"
        self.__icon = ""
        self.__animation = ""
        if self.__baseWidget:
            self.__initColorByBaseWidget()
        else:
            self.__hover_color = DEFAULT_BUTTON_HOVER_COLOR
            self.__pressed_color = DEFAULT_BUTTON_PRESSED_COLOR
            self.__checked_color = DEFAULT_BUTTON_CHECKED_COLOR

    def __initColorByBaseWidget(self):
        self.__base_color = self.__baseWidget.palette().color(QPalette.ColorRole.Base)
        self.__hover_color = self.__getHoverColor(self.__base_color)
        self.__pressed_color = self.__getPressedColor(self.__base_color)
        self.__checked_color = self.__getPressedColor(self.__base_color)

    def __getColorByFactor(self, base_color, factor):
        r, g, b = base_color.red(), base_color.green(), base_color.blue()
        gray = qGray(r, g, b)
        if gray > 255 // 2:
            color = base_color.darker(factor)
        else:
            color = base_color.lighter(factor)
        return color

    def __getHoverColor(self, base_color):
        hover_factor = 120
        hover_color = self.__getColorByFactor(base_color, hover_factor)
        return hover_color.name()

    def __getPressedColor(self, base_color):
        pressed_factor = 130
        pressed_color = self.__getColorByFactor(base_color, pressed_factor)
        return pressed_color.name()

    def __getCheckedColor(self, base_color):
        return self.__getPressedColor(self.__base_color)

    def __getButtonTextColor(self, base_color):
        r, g, b = (
            base_color.red() ^ 255,
            base_color.green() ^ 255,
            base_color.blue() ^ 255,
        )
        if r == g == b:
            text_color = QColor(r, g, b)
        elif qGray(r, g, b) > 255 // 2:
            text_color = QColor(255, 255, 255)
        else:
            text_color = QColor(0, 0, 0)
        return text_color.name()

    def styleInit(self):
        self.__btn_style = f"""
        QAbstractButton
        {{
        border: 0;
        width: {self.__size}px;
        height: {self.__size}px;
        background-color: {self.__background_color};
        border-radius: {self.__border_radius}px;
        padding: {self.__padding}px;
        }}
        QAbstractButton:hover
        {{
        background-color: {self.__hover_color};
        }}
        QAbstractButton:pressed
        {{
        background-color: {self.__pressed_color};
        }}
        QAbstractButton:checked
        {{
        background-color: {self.__checked_color};
        border: none;
        }}
        """
        return self.__btn_style

    def setPadding(self, padding: int):
        self.__padding = padding

    def setBorderRadius(self, border_radius: int):
        self.__border_radius = border_radius

    def setBackground(self, background=None):
        if background:
            self.__background_color = background
        else:
            self.__background_color = self.__base_color.name()

    def setAsCircle(self, height):
        self.__border_radius = height // 2

    def __scaleChanged(self, dpi):
        self.__size = dpi // 4
