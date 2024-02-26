from PyQt5.QtWidgets import QGroupBox
from qtpy.QtGui import QFont, QColor
from qtpy.QtWidgets import QWidget, QVBoxLayout

from pyqt_openai.theme.qt_sass_theme.qtSassTheme import QtSassTheme
from pyqt_openai.widgets.pyqt_color_picker import ColorPickerWidget
from pyqt_openai.widgets.pyqt_font_dialog.fontWidget import FontWidget


class ThemeWidget(QWidget):
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
        # TODO translation
        themeGroupBox = QGroupBox()
        themeGroupBox.setTitle('Theme')

        lay = QVBoxLayout()
        self.__fontWidget = FontWidget()
        self.__fontWidget.fontChanged.connect(self.__fontChanged)
        self.__fontWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.__currentFont = self.__fontWidget.getFont()

        self.__colorPicker = ColorPickerWidget(orientation='vertical')
        self.__colorPicker.colorChanged.connect(self.__colorChanged)
        self.__currentColor = self.__colorPicker.getCurrentColor().name()

        lay.addWidget(self.__fontWidget)
        lay.addWidget(self.__colorPicker)

        themeGroupBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(themeGroupBox)

        self.setLayout(lay)

    def getColor(self):
        return self.__currentColor

    def getFont(self):
        return self.__currentFont

    def setColor(self, color):
        self.__currentColor = color

    def setFont(self, font):
        self.__currentFont = font

    # def __setSampleStyle(self):
    #     self.__theme.getThemeFiles(theme=self.__currentColor, font=self.__currentFont)
    #     self.__theme.setThemeFiles(main_window=self.__widgetToControl)

    # def setWidgetToControl(self, widget: QWidget):
    #     self.__widgetToControl = widget
    #     self.__setSampleStyle()

    def __fontChanged(self, font: QFont):
        self.__currentFont = font
        # self.__setSampleStyle()

    def __colorChanged(self, color: QColor):
        self.__currentColor = color.name()
        # self.__setSampleStyle()