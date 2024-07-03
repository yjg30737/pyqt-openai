import os.path, posixpath

from qtpy.QtGui import QColor, QPalette, qGray, QIcon
from qtpy.QtWidgets import QGraphicsColorizeEffect, QWidget, QApplication, QPushButton

from pyqt_openai.pyqt_openai_data import ROOT_DIR


class Button(QPushButton):
    def __init__(self, base_widget: QWidget = None, parent=None):
        super().__init__(parent)
        self.__baseWidget = base_widget
        self.__initVal()
        self.__styleInit()

    def __initVal(self):
        # to set size accordance with scale
        sc = QApplication.screens()[0]
        sc.logicalDotsPerInchChanged.connect(self.__scaleChanged)
        self.__size = sc.logicalDotsPerInch() // 4
        self.__padding = self.__border_radius = self.__size // 10
        self.__background_color = 'transparent'
        self.__icon = ''
        self.__animation = ''
        self.installEventFilter(self)
        if self.__baseWidget:
            self.__baseWidget.installEventFilter(self)
            self.__initColorByBaseWidget()
        else:
            self.__hover_color = '#DDDDDD'
            self.__pressed_color = '#FFFFFF'
            self.__checked_color = '#CCCCCC'
            self.__text_color = '#AAAAAA'

    def __initColorByBaseWidget(self):
        self.__base_color = self.__baseWidget.palette().color(QPalette.ColorRole.Base)
        self.__hover_color = self.__getHoverColor(self.__base_color)
        self.__pressed_color = self.__getPressedColor(self.__base_color)
        self.__checked_color = self.__getPressedColor(self.__base_color)
        self.__text_color = self.__getButtonTextColor(self.__base_color)

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
        return self.__getPressedColor(base_color)

    def __getButtonTextColor(self, base_color):
        r, g, b = base_color.red() ^ 255, base_color.green() ^ 255, base_color.blue() ^ 255
        if r == g == b:
            text_color = QColor(r, g, b)
        else:
            if qGray(r, g, b) > 255 // 2:
                text_color = QColor(255, 255, 255)
            else:
                text_color = QColor(0, 0, 0)
        return text_color.name()

    def __styleInit(self):
        self.__btn_style = f'''
        QAbstractButton
        {{
        border: 0;
        width: {self.__size};
        height: {self.__size};
        background-color: {self.__background_color};
        border-radius: {self.__border_radius};
        padding: {self.__padding};
        color: {self.__text_color};
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
        '''

        self.setStyleSheet(self.__btn_style)

    def setStyleAndIcon(self, icon: str):
        self.__icon = os.path.join(ROOT_DIR, icon).replace(os.sep, posixpath.sep)
        self.__styleInit()
        self.setIcon(QIcon(self.__icon))

    def eventFilter(self, obj, e):
        if obj == self:
            # to change grayscale when button gets disabled
            # if button get enabled/disabled EnableChange will emit
            # so catch the EnabledChange
            if e.type() == 98:
                # change to enabled state
                effect = QGraphicsColorizeEffect()
                effect.setColor(QColor(255, 255, 255))
                if self.isEnabled():
                    effect.setStrength(0)
                else:
                    effect.setStrength(1)
                    effect.setColor(QColor(150, 150, 150))
                self.setGraphicsEffect(effect)
        if obj == self.__baseWidget:
            # catch the StyleChange event of base widget
            if e.type() == 100:
                # if base widget's background is transparent (#ffffff)
                if self.__baseWidget.palette().color(QPalette.ColorRole.Base).name() == '#ffffff':
                    # then check the parent widget's background
                    if self.__baseWidget.parent():
                        if self.__baseWidget.parent().palette().color(QPalette.ColorRole.Base).name() == '#ffffff':
                            pass
                        else:
                            self.__baseWidget = self.__baseWidget.parent()
                self.__initColorByBaseWidget()
                self.__styleInit()
        return super().eventFilter(obj, e)

    def setPadding(self, padding: int):
        self.__padding = padding
        self.__styleInit()

    def setBorderRadius(self, border_radius: int):
        self.__border_radius = border_radius
        self.__styleInit()

    def setBackground(self, background=None):
        if background:
            self.__background_color = background
        else:
            self.__background_color = self.__base_color.name()
        self.__styleInit()

    def setAsCircle(self):
        self.setBorderRadius(self.height() // 2)
        self.__styleInit()

    # to set size accordance with scale
    def __scaleChanged(self, dpi):
        self.__size = dpi // 4
        self.__styleInit()