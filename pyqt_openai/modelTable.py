from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt


class ModelTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setColumnCount(2)
        self.setRowCount(10)
        self.resizeColumnsToContents()
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        item = QTableWidgetItem('Allow Fine Tuning')
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(0, 0, item)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # TODO set more attributes
    # currently set the allow_fine_tuning only
    def setModelInfo(self, info):
        print(info)