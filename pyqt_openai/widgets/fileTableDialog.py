from PySide6.QtWidgets import QDialog, QTableWidget, QHeaderView, QVBoxLayout


# TODO v1.8.0
class FileTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # TODO LANGUAGE
        self.setWindowTitle("File List (Working)")
        # File tables
        self.__fileTable = QTableWidget()
        self.__fileTable.setColumnCount(2)
        self.__fileTable.setHorizontalHeaderLabels(["File Name", "Type"])
        self.__fileTable.setColumnWidth(0, 300)
        self.__fileTable.setColumnWidth(1, 100)
        self.__fileTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.__fileTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.__fileTable.setSelectionMode(QTableWidget.SingleSelection)
        self.__fileTable.setSortingEnabled(True)
        self.__fileTable.setAlternatingRowColors(True)
        self.__fileTable.setShowGrid(False)
        self.__fileTable.verticalHeader().hide()
        self.__fileTable.horizontalHeader().setStretchLastSection(True)
        self.__fileTable.horizontalHeader().setHighlightSections(False)
        self.__fileTable.horizontalHeader().setSectionsClickable(True)
        self.__fileTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.__fileTable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        lay = QVBoxLayout()
        lay.addWidget(self.__fileTable)
        self.setLayout(lay)
