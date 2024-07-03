"""
This dialog is for exporting conversation threads or images selected by the user from the history.
"""
from qtpy.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QWidget, QCheckBox, QPushButton, QFileDialog, QLabel, QFrame
from qtpy.QtGui import QIcon
from qtpy.QtCore import Qt
from pyqt_openai.widgets.button import Button


class ExportDialog(QDialog):
    def __init__(self, columns, table_nm, parent=None):
        super(ExportDialog, self).__init__(parent)
        self.__initVal(columns, table_nm)
        self.__initUi()

    def __initVal(self, columns, table_nm):
        self.__columns = columns
        self.__table_nm = table_nm

    def __initUi(self):
        self.setWindowTitle("Export")
        self.setWindowIcon(QIcon("ico/export.svg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)