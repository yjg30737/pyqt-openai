from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidgetItem


class FontItemWidget(QWidget):
    fontItemChanged = pyqtSignal(str, QFontDatabase)

    def __init__(self, font: QFont = QFont('Arial', 10)):
        super().__init__()
        self.__font_families = []
        self.__initUi(font=font)

    def __initUi(self, font: QFont):
        self.__fontLineEdit = QLineEdit()
        self.__fontLineEdit.textEdited.connect(self.__textEdited)

        self.__fontListWidget = QListWidget()
        self.__initFonts(font)
        self.__fontListWidget.itemSelectionChanged.connect(self.__fontItemChanged)

        lay = QVBoxLayout()
        lay.addWidget(self.__fontLineEdit)
        lay.addWidget(self.__fontListWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        fontBottomWidget = QWidget()
        fontBottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(QLabel('Font'))
        lay.addWidget(fontBottomWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.setLayout(lay)

    def __initFonts(self, font: QFont):
        self.__initFontsList()
        self.__initCurrentFont(font=font)

    def __initFontsList(self):
        fd = QFontDatabase()
        fm = fd.families(QFontDatabase.Any)
        self.__font_families.extend(fm)
        self.__fontListWidget.addItems(fm)

    def __initCurrentFont(self, font: QFont):
        items = self.__fontListWidget.findItems(font.family(), Qt.MatchFixedString)
        item = QListWidgetItem()
        if items:
            item = items[0]
        else:
            item = self.__fontListWidget.item(0)
        self.__fontListWidget.setCurrentItem(item)
        font_name = item.text()
        self.__fontLineEdit.setText(font_name)

    def __fontItemChanged(self):
        font_name = self.__fontListWidget.currentItem().text()
        self.__fontLineEdit.setText(font_name)
        fd = QFontDatabase()
        self.fontItemChanged.emit(font_name, fd)

    def __textEdited(self):
        self.__fontListWidget.clear()
        text = self.__fontLineEdit.text()
        if text.strip() != '':
            match_families = []
            for family in self.__font_families:
                if family.startswith(text):
                    match_families.append(family)
            if match_families:
                self.__fontListWidget.addItems(match_families)
            else:
                pass
        else:
            self.__fontListWidget.addItems(self.__font_families)

    def getFontFamily(self):
        item = self.__fontListWidget.currentItem()
        if item:
            return item.text()
        else:
            return 'Arial'