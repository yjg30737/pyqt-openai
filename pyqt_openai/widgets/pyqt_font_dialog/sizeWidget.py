from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidgetItem


class SizeWidget(QWidget):
    sizeItemChanged = pyqtSignal(int)

    def __init__(self, font: QFont = QFont('Arial', 10)):
        super().__init__()
        self.__initUi(font=font)

    def __initUi(self, font: QFont):
        self.__sizeLineEdit = QLineEdit()
        self.__sizeLineEdit.textEdited.connect(self.__textEdited)

        self.__sizeListWidget = QListWidget()
        self.__initSizes(font=font)
        self.__sizeListWidget.itemSelectionChanged.connect(self.__sizeItemChanged)

        lay = QVBoxLayout()
        lay.addWidget(self.__sizeLineEdit)
        lay.addWidget(self.__sizeListWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        sizeBottomWidget = QWidget()
        sizeBottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('Size'))
        lay.addWidget(sizeBottomWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.setLayout(lay)

    def __initSizes(self, font: QFont):
        self.__initSizesList(font=font)
        self.__initCurrentSize(font=font)

    def __initSizesList(self, font: QFont):
        fd = QFontDatabase()
        font_name = font.family()
        style_name = fd.styles(font_name)
        # In case of font is not in the font list
        if style_name:
            style_name = style_name[0]
        else:
            font_name = 'Arial'
            style_name = fd.styles(font_name)[0]
        sizes = fd.pointSizes(font_name, style_name)
        sizes = list(map(str, sizes))
        self.__sizeListWidget.addItems(sizes)

    def __initCurrentSize(self, font: QFont):
        items = self.__sizeListWidget.findItems(str(font.pointSize()), Qt.MatchFixedString)
        item = QListWidgetItem()
        if items:
            item = items[0]
        else:
            item = self.__sizeListWidget.item(0)
        self.__sizeListWidget.setCurrentItem(item)
        size_text = item.text()
        self.__sizeLineEdit.setText(size_text)

    def __textEdited(self):
        size_text = self.__sizeLineEdit.text()
        items = self.__sizeListWidget.findItems(size_text, Qt.MatchFixedString)
        if items:
            self.__sizeListWidget.setCurrentItem(items[0])
        self.sizeItemChanged.emit(int(size_text))

    def __sizeItemChanged(self):
        size_text = self.__sizeListWidget.currentItem().text()
        self.sizeItemChanged.emit(int(size_text))
        self.__sizeLineEdit.setText(size_text)

    def setSizes(self, sizes, prev_size=10):
        sizes = list(map(str, sizes))
        self.__sizeListWidget.clear()
        self.__sizeListWidget.addItems(sizes)
        items = self.__sizeListWidget.findItems(str(prev_size), Qt.MatchFixedString)
        if len(items) > 0:
            item = items[0]
            self.__sizeListWidget.setCurrentItem(item)
            self.__sizeLineEdit.setText(item.text())
        else:
            self.__sizeLineEdit.setText(str(prev_size))

    def getSize(self):
        return self.__sizeListWidget.currentItem().text()