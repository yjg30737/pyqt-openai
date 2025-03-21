from __future__ import annotations

from qtpy.QtCore import QThread, Qt, Signal
from qtpy.QtGui import QFont, QFontDatabase
from qtpy.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

from pyqt_openai import DEFAULT_FONT_FAMILY
from pyqt_openai.lang.translations import LangClass


class FontLoaderThread(QThread):
    fonts_loaded = Signal(list)
    afterFinished = Signal(QFont)

    def __init__(
        self,
        font: QFont,
    ) -> None:
        super().__init__()
        self.font: QFont = font

    def run(self):
        fm: list[str] = QFontDatabase.families(QFontDatabase.WritingSystem.Any)
        self.fonts_loaded.emit(fm)
        self.afterFinished.emit(self.font)


class SizeWidget(QWidget):
    sizeItemChanged: Signal = Signal(int)

    def __init__(
        self,
        font: QFont,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.__initUi(font=font)

    def __initUi(
        self,
        font: QFont,
    ) -> None:
        self.__sizeLineEdit: QLineEdit = QLineEdit()
        self.__sizeLineEdit.textEdited.connect(self.__textEdited)

        self.__sizeListWidget: QListWidget = QListWidget()
        self.__initSizes(font=font)
        self.__sizeListWidget.itemSelectionChanged.connect(self.__sizeItemChanged)

        lay = QVBoxLayout()
        lay.addWidget(self.__sizeLineEdit)
        lay.addWidget(self.__sizeListWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        sizeBottomWidget: QWidget = QWidget()
        sizeBottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Size"]))
        lay.addWidget(sizeBottomWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.setLayout(lay)

    def __initSizes(
        self,
        font: QFont,
    ) -> None:
        self.__initSizesList(font=font)
        self.setCurrentSize(font=font)

    def __initSizesList(
        self,
        font: QFont,
    ) -> None:
        font_name: str = font.family()
        style_name: list[str] = QFontDatabase.styles(font_name)
        # In case of font is not in the font list
        if style_name:
            pass
        else:
            font_name = "Arial"
        sizes = QFontDatabase.pointSizes(font_name)
        sizes = list(map(str, sizes))
        self.__sizeListWidget.addItems(sizes)

    def setCurrentSize(
        self,
        font: QFont,
    ) -> None:
        items = self.__sizeListWidget.findItems(
            str(font.pointSize()), Qt.MatchFlag.MatchFixedString,
        )
        item = QListWidgetItem()
        if items:
            item = items[0]
        else:
            item = self.__sizeListWidget.item(0)
        if item:
            self.__sizeListWidget.setCurrentItem(item)
            size_text = item.text()
            self.__sizeLineEdit.setText(size_text)
        else:
            item = QListWidgetItem("10")
            self.__sizeListWidget.setCurrentItem(item)
            size_text = item.text()
            self.__sizeLineEdit.setText(size_text)

    def __textEdited(self):
        size_text = self.__sizeLineEdit.text()
        items: list[QListWidgetItem] = self.__sizeListWidget.findItems(
            size_text, Qt.MatchFlag.MatchFixedString,
        )
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
        items = self.__sizeListWidget.findItems(
            str(prev_size), Qt.MatchFlag.MatchFixedString,
        )
        if len(items) > 0:
            item = items[0]
            self.__sizeListWidget.setCurrentItem(item)
            self.__sizeLineEdit.setText(item.text())
        else:
            self.__sizeLineEdit.setText(str(prev_size))

    def getSize(self):
        return (
            self.__sizeListWidget.currentItem().text()
            if self.__sizeListWidget.currentItem()
            else 10
        )


class FontItemWidget(QWidget):
    fontItemChanged = Signal(str, list, list)

    def __init__(self, font, parent=None):
        super().__init__(parent)
        self.__font_families: list[str] = []
        self.__initUi(font=font)

    def __initUi(
        self,
        font: QFont,
    ) -> None:
        self.__fontLineEdit: QLineEdit = QLineEdit()
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
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Font"]))
        lay.addWidget(fontBottomWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.setLayout(lay)

    def __initFonts(
        self,
        font: QFont,
    ) -> None:
        self.loader_thread: FontLoaderThread = FontLoaderThread(font)
        self.loader_thread.fonts_loaded.connect(self.__onFontsLoaded)
        self.loader_thread.start()
        self.loader_thread.afterFinished.connect(self.setCurrentFont)

    def __onFontsLoaded(
        self,
        fm: list[str],
    ) -> None:
        self.__font_families.extend(fm)
        # Set each item to each font family
        for f in fm:
            item = QListWidgetItem(f)
            # FIXME This makes the font list widget too slow
            # item.setFont(QFont(f))
            self.__fontListWidget.addItem(item)

    def setCurrentFont(self, font: QFont):
        items = self.__fontListWidget.findItems(
            font.family(), Qt.MatchFlag.MatchFixedString,
        )
        item = QListWidgetItem()
        if items:
            item = items[0]
        else:
            item = self.__fontListWidget.item(0)
        self.__fontListWidget.setCurrentItem(item)
        font_name = item.text()
        self.__fontLineEdit.setText(font_name)

    def __fontItemChanged(self):
        font_name: str = self.__fontListWidget.currentItem().text()
        self.__fontLineEdit.setText(font_name)
        styles: list[str] = QFontDatabase.styles(font_name)
        pointSizes: list[int] = QFontDatabase.pointSizes(
            font_name,
            QFontDatabase.styles(font_name)[0],
        )
        self.fontItemChanged.emit(font_name, styles, pointSizes)

    def __textEdited(self):
        self.__fontListWidget.clear()
        text = self.__fontLineEdit.text()
        if text.strip() != "":
            match_families: list[str] = []
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
        return DEFAULT_FONT_FAMILY


class FontWidget(QWidget):
    fontChanged = Signal(QFont)

    def __init__(
        self,
        font: QFont,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.__current_font: QFont = font
        self.__initUi(font=font)

    def __initUi(
        self,
        font: QFont,
    ) -> None:
        self.__previewTextEdit: QTextEdit = QTextEdit(self)
        self.__previewTextEdit.textChanged.connect(self.__textChanged)

        self.__fontItemWidget: FontItemWidget = FontItemWidget(font)
        self.__fontItemWidget.fontItemChanged.connect(self.__fontItemChangedExec)

        self.__sizeWidget: SizeWidget = SizeWidget(font)
        self.__sizeWidget.sizeItemChanged.connect(self.__sizeItemChangedExec)

        self.__initPreviewTextEdit()

        lay = QHBoxLayout()
        lay.addWidget(self.__fontItemWidget)
        lay.addWidget(self.__sizeWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS["Preview"]))
        lay.addWidget(self.__previewTextEdit)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)
        bottomWidget.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Preferred,
        )

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(bottomWidget)
        self.setLayout(lay)

    def __initPreviewTextEdit(self) -> None:
        font_family: str = self.__fontItemWidget.getFontFamily()
        font_size: int = self.__sizeWidget.getSize()
        font: QFont = self.__previewTextEdit.currentFont()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        self.__previewTextEdit.setCurrentFont(font)
        self.__previewTextEdit.setText(LangClass.TRANSLATIONS["Sample"])

    def __sizeItemChangedExec(self, size: int) -> None:
        self.__previewTextEdit.selectAll()
        font: QFont = self.__previewTextEdit.currentFont()
        font.setPointSize(size)
        self.__previewTextEdit.setCurrentFont(font)

        self.__current_font: QFont = font
        self.fontChanged.emit(self.__current_font)

    def __fontItemChangedExec(
        self,
        font_text: str,
        styles: list[str],
        sizes: list[int],
    ) -> None:
        self.__previewTextEdit.selectAll()
        font: QFont = self.__previewTextEdit.currentFont()
        prev_size: int = font.pointSize()

        font.setFamily(font_text)

        sizes = list(filter(lambda x: x <= 20 and x >= 8, sizes))

        if prev_size in sizes:
            self.__sizeWidget.setSizes(sizes, prev_size)
            font.setPointSize(prev_size)
        else:
            self.__sizeWidget.setSizes(sizes, prev_size)

        self.__previewTextEdit.setCurrentFont(font)
        self.__current_font = font
        self.fontChanged.emit(self.__current_font)

    def getFont(self):
        return self.__previewTextEdit.currentFont()

    def setCurrentFont(
        self,
        font: QFont,
    ) -> None:
        self.__fontItemWidget.setCurrentFont(font=font)
        self.__sizeWidget.setCurrentSize(font=font)

        self.__previewTextEdit.setCurrentFont(font)
        self.__current_font = font
        self.fontChanged.emit(self.__current_font)

    def __textChanged(self):
        text = self.__previewTextEdit.toPlainText()
        if text.strip() != "":
            pass
        else:
            self.__previewTextEdit.setCurrentFont(self.__current_font)
