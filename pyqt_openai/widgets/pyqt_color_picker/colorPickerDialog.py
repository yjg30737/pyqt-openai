from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

from widgets.pyqt.pyqt_color_picker.colorPickerWidget import ColorPickerWidget


class ColorPickerDialog(QDialog):
    def __init__(self, color=QColor(255, 255, 255), orientation='horizontal'):
        super().__init__()
        if isinstance(color, QColor):
            pass
        elif isinstance(color, str):
            color = QColor(color)
        self.__initUi(color=color, orientation=orientation)

    def __initUi(self, color, orientation):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle('Pick the color')

        self.__colorPickerWidget = ColorPickerWidget(color, orientation)

        okBtn = QPushButton('OK')
        cancelBtn = QPushButton('Cancel')

        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.close)

        if orientation == 'horizontal':
            lay = QHBoxLayout()
            lay.addWidget(self.__colorPickerWidget)
            lay.setContentsMargins(0, 0, 0, 0)

            topWidget = QWidget()
            topWidget.setLayout(lay)

            lay = QHBoxLayout()
            lay.setAlignment(Qt.AlignRight)
            lay.addWidget(okBtn)
            lay.addWidget(cancelBtn)
            lay.setContentsMargins(0, 0, 0, 0)

            bottomWidget = QWidget()
            bottomWidget.setLayout(lay)

            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setFrameShadow(QFrame.Sunken)
            sep.setContentsMargins(0, 0, 0, 0)

            lay = QVBoxLayout()
            lay.addWidget(topWidget)
            lay.addWidget(sep)
            lay.addWidget(bottomWidget)
        elif orientation == 'vertical':
            lay = QHBoxLayout()
            lay.addWidget(self.__colorPickerWidget)
            lay.setContentsMargins(0, 0, 0, 0)

            leftWidget = QWidget()
            leftWidget.setLayout(lay)

            lay = QVBoxLayout()
            lay.setAlignment(Qt.AlignBottom)
            lay.addWidget(okBtn)
            lay.addWidget(cancelBtn)
            lay.setContentsMargins(0, 0, 0, 0)

            rightWidget = QWidget()
            rightWidget.setLayout(lay)

            sep = QFrame()
            sep.setFrameShape(QFrame.VLine)
            sep.setFrameShadow(QFrame.Sunken)
            sep.setContentsMargins(0, 0, 0, 0)

            lay = QHBoxLayout()
            lay.addWidget(leftWidget)
            lay.addWidget(sep)
            lay.addWidget(rightWidget)

        self.setLayout(lay)

    def accept(self) -> None:
        return super().accept()

    def getColor(self) -> QColor:
        return self.__colorPickerWidget.getCurrentColor()

    # def getWidget(self):
    #     return self.__colorPickerWidget