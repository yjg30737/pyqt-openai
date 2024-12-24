from __future__ import annotations

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QWidget

from pyqt_openai import ICON_SEARCH
from pyqt_openai.widgets.svgLabel import SvgLabel


class SearchBar(QWidget):
    searched = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        # search bar label
        self.__label: QLabel = QLabel()

        self._initUi()

    def _initUi(self):
        self.__searchLineEdit: QLineEdit = QLineEdit()
        self.__searchIconLbl: SvgLabel = SvgLabel()
        ps = QApplication.font().pointSize()
        self.__searchIconLbl.setFixedSize(ps, ps)

        self.__searchBar: QWidget = QWidget()
        self.__searchBar.setObjectName("searchBar")

        lay = QHBoxLayout()
        lay.addWidget(self.__searchIconLbl)
        lay.addWidget(self.__searchLineEdit)
        self.__searchBar.setLayout(lay)
        lay.setContentsMargins(ps // 2, 0, 0, 0)
        lay.setSpacing(0)

        self.__searchLineEdit.setFocus()
        self.__searchLineEdit.textChanged.connect(self.__searched)

        self.setAutoFillBackground(True)

        lay = QHBoxLayout()
        lay.addWidget(self.__searchBar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        self._topWidget: QWidget = QWidget()
        self._topWidget.setLayout(lay)

        lay = QGridLayout()
        lay.addWidget(self._topWidget)

        searchWidget: QWidget = QWidget()
        searchWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        lay = QGridLayout()
        lay.addWidget(searchWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)

        self.__setStyle()

        self.setLayout(lay)

    # ex) searchBar.setLabel(True, 'Search Text')
    def setLabel(
        self,
        visibility: bool = True,
        text: str | None = None,
    ):
        if text:
            self.__label.setText(text)
        self.__label.setVisible(visibility)

    def __setStyle(self):
        self.__searchIconLbl.setSvgFile(ICON_SEARCH)
        self.setStyleSheet(
            """
            QLineEdit
            {
                background: transparent;
                border: none;
            }
            QWidget#searchBar
            {
                border: 1px solid gray;
            }
            QWidget { padding: 5px; }
            """,
        )

    def __searched(self, text: str):
        self.searched.emit(text)

    def setSearchIcon(
        self,
        icon_filename: str,
    ):
        self.__searchIconLbl.setSvgFile(icon_filename)

    def setPlaceHolder(
        self,
        text: str,
    ):
        self.__searchLineEdit.setPlaceholderText(text)

    def getSearchBar(self) -> QLineEdit:
        return self.__searchLineEdit

    def getSearchLabel(self) -> SvgLabel:
        return self.__searchIconLbl
