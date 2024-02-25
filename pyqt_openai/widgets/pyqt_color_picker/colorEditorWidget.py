from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QLineEdit


class ColorEditorWidget(QWidget):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, color, orientation):
        super().__init__()
        self.__current_color = color
        self.__initVal()
        self.__initUi(color, orientation)

    def __initVal(self):
        # default width and height
        self.__w = 200
        self.__h = 75

    def __initUi(self, color, orientation):
        self.__colorPreviewWithGraphics = QWidget()
        self.__colorPreviewWithGraphics.setFixedWidth(self.__w)
        self.__colorPreviewWithGraphics.setMinimumHeight(self.__h)
        self.setColorPreviewWithGraphics()

        self.__hLineEdit = QLineEdit()
        self.__hLineEdit.setReadOnly(True)

        self.__rSpinBox = QSpinBox()
        self.__gSpinBox = QSpinBox()
        self.__bSpinBox = QSpinBox()

        self.__rSpinBox.valueChanged.connect(self.__rColorChanged)
        self.__gSpinBox.valueChanged.connect(self.__gColorChanged)
        self.__bSpinBox.valueChanged.connect(self.__bColorChanged)

        self.__hLineEdit.setAlignment(Qt.AlignCenter)
        self.__hLineEdit.setFont(QFont('Arial', 12))

        spinBoxs = [self.__rSpinBox, self.__gSpinBox, self.__bSpinBox]
        for spinBox in spinBoxs:
            spinBox.setRange(0, 255)
            spinBox.setAlignment(Qt.AlignCenter)
            spinBox.setFont(QFont('Arial', 12))

        lay = QFormLayout()
        lay.addRow('#', self.__hLineEdit)
        lay.addRow('R', self.__rSpinBox)
        lay.addRow('G', self.__gSpinBox)
        lay.addRow('B', self.__bSpinBox)
        lay.setContentsMargins(0, 0, 0, 0)

        colorEditor = QWidget()
        colorEditor.setLayout(lay)
        if orientation == 'horizontal':
            lay = QVBoxLayout()
        elif orientation == 'vertical':
            lay = QHBoxLayout()
        lay.addWidget(self.__colorPreviewWithGraphics)
        lay.addWidget(colorEditor)

        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self.setColor(color)

    def setColorPreviewWithGraphics(self):
        self.__colorPreviewWithGraphics.setStyleSheet(f' border-radius: 5px; '
                                                      f'background-color: {self.__current_color.name()}; ')

    def setColor(self, color):
        self.__current_color = color
        self.setColorPreviewWithGraphics()
        self.__hLineEdit.setText(self.__current_color.name())

        # Prevent infinite valueChanged event loop
        self.__rSpinBox.valueChanged.disconnect(self.__rColorChanged)
        self.__gSpinBox.valueChanged.disconnect(self.__gColorChanged)
        self.__bSpinBox.valueChanged.disconnect(self.__bColorChanged)

        r, g, b = self.__current_color.red(), self.__current_color.green(), self.__current_color.blue()

        self.__rSpinBox.setValue(r)
        self.__gSpinBox.setValue(g)
        self.__bSpinBox.setValue(b)

        self.__rSpinBox.valueChanged.connect(self.__rColorChanged)
        self.__gSpinBox.valueChanged.connect(self.__gColorChanged)
        self.__bSpinBox.valueChanged.connect(self.__bColorChanged)

    def __rColorChanged(self, r):
        self.__current_color.setRed(r)
        self.__procColorChanged()

    def __gColorChanged(self, g):
        self.__current_color.setGreen(g)
        self.__procColorChanged()

    def __bColorChanged(self, b):
        self.__current_color.setBlue(b)
        self.__procColorChanged()

    def __procColorChanged(self):
        self.__hLineEdit.setText(self.__current_color.name())
        self.setColorPreviewWithGraphics()
        self.colorChanged.emit(self.__current_color)

    def getCurrentColor(self):
        return self.__current_color