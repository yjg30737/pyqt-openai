from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpinBox, QVBoxLayout, QFrame, QLabel

from theme.qt_sass_theme import QtSassTheme
from widgets.pyqt.pyqt_color_picker import ColorPickerWidget
from widgets.pyqt.pyqt_font_dialog.fontWidget import FontWidget


class RightWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__theme = QtSassTheme()
        self.__currentColor = ''
        self.__currentFont = ''
        self.__widgetToControl = ''

    def __initUi(self):
        lay = QVBoxLayout()
        fontWidget = FontWidget()
        fontWidget.fontChanged.connect(self.__fontChanged)
        fontWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.__currentFont = fontWidget.getFont()

        self.__colorPicker = ColorPickerWidget(orientation='vertical')
        self.__colorPicker.colorChanged.connect(self.__colorChanged)
        self.__currentColor = self.__colorPicker.getCurrentColor().name()

        lay.addWidget(fontWidget)
        lay.addWidget(self.__colorPicker)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def __setSampleStyle(self):
        self.__theme.getThemeFiles(theme=self.__currentColor, font=self.__currentFont)
        self.__theme.setThemeFiles(main_window=self.__widgetToControl)

    def setWidgetToControl(self, widget: QWidget):
        self.__widgetToControl = widget
        self.__setSampleStyle()

    def __fontChanged(self, font: QFont):
        self.__currentFont = font
        self.__setSampleStyle()

    def __colorChanged(self, color: QColor):
        self.__currentColor = color.name()
        self.__setSampleStyle()