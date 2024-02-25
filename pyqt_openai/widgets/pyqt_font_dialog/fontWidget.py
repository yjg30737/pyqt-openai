from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QSizePolicy, \
    QTextEdit, QVBoxLayout, QWidget, QHBoxLayout

from .fontItemWidget import FontItemWidget
from .sizeWidget import SizeWidget
from .styleWidget import StyleWidget


class FontWidget(QWidget):
    fontChanged = pyqtSignal(QFont)

    def __init__(self, font: QFont = QFont('Arial', 10)):
        super().__init__()
        self.__current_font = font
        self.__initUi(font=font)

    def __initUi(self, font: QFont):
        self.__previewTextEdit = QTextEdit()
        self.__previewTextEdit.textChanged.connect(self.__textChanged)

        self.__fontItemWidget = FontItemWidget(font)
        self.__fontItemWidget.fontItemChanged.connect(self.__fontItemChangedExec)

        self.__sizeWidget = SizeWidget(font)
        self.__sizeWidget.sizeItemChanged.connect(self.__sizeItemChangedExec)

        self.__styleWidget = StyleWidget(font)
        self.__styleWidget.boldChecked.connect(self.__setBold)
        self.__styleWidget.italicChecked.connect(self.__setItalic)

        self.__initPreviewTextEdit()

        lay = QHBoxLayout()
        lay.addWidget(self.__fontItemWidget)
        lay.addWidget(self.__sizeWidget)
        lay.addWidget(self.__styleWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('Preview'))
        lay.addWidget(self.__previewTextEdit)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)
        bottomWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(bottomWidget)
        self.setLayout(lay)

    def __initPreviewTextEdit(self):
        font_family = self.__fontItemWidget.getFontFamily()
        font_size = self.__sizeWidget.getSize()
        bold_f = self.__styleWidget.isBold()
        italic_f = self.__styleWidget.isItalic()
        font = self.__previewTextEdit.currentFont()
        font.setFamily(font_family)
        font.setPointSize(int(font_size))
        font.setBold(bold_f)
        font.setItalic(italic_f)
        self.__previewTextEdit.setCurrentFont(font)
        self.__previewTextEdit.setText('Sample')

    def __setBold(self, f: int):
        self.__previewTextEdit.selectAll()
        font = self.__previewTextEdit.currentFont()
        font.setBold(f)
        self.__previewTextEdit.setCurrentFont(font)
        self.__current_font = font
        self.fontChanged.emit(self.__current_font)

    def __setItalic(self, f: bool):
        self.__previewTextEdit.selectAll()
        font = self.__previewTextEdit.currentFont()
        font.setItalic(f)
        self.__previewTextEdit.setCurrentFont(font)
        self.__current_font = font
        self.fontChanged.emit(self.__current_font)

    def __sizeItemChangedExec(self, size):
        self.__previewTextEdit.selectAll()
        font = self.__previewTextEdit.currentFont()
        font.setPointSize(size)
        self.__previewTextEdit.setCurrentFont(font)
        self.__current_font = font
        self.fontChanged.emit(self.__current_font)

    def __fontItemChangedExec(self, font_text, fd):
        self.__previewTextEdit.selectAll()
        font = self.__previewTextEdit.currentFont()
        prev_size = font.pointSize()
        styles = fd.styles(font_text)

        font.setFamily(font_text)

        sizes = fd.pointSizes(font_text, styles[0])
        if prev_size in sizes:
            self.__sizeWidget.setSizes(sizes, prev_size)
            font.setPointSize(prev_size)
        else:
            self.__sizeWidget.setSizes(sizes, prev_size)
            # font.setPointSize(sizes[0])

        self.__previewTextEdit.setCurrentFont(font)
        self.__current_font = font
        self.fontChanged.emit(self.__current_font)

    def getFont(self):
        return self.__previewTextEdit.currentFont()

    def __textChanged(self):
        text = self.__previewTextEdit.toPlainText()
        if text.strip() != '':
            pass
        else:
            self.__previewTextEdit.setCurrentFont(self.__current_font)