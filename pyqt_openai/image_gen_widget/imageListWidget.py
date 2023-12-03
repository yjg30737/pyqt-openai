from PyQt5.QtWidgets import QWidget, QTableWidget


class ImageListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        
        tableWidget = QTableWidget()