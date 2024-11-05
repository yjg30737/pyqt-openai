from PySide6.QtWidgets import QDialog


class FileTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        pass