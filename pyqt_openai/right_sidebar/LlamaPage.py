import platform
import subprocess

from qtpy.QtCore import Qt, QSettings
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QWidget, QComboBox, QLabel, QVBoxLayout, QCheckBox, QDoubleSpinBox, \
    QSpinBox, QFormLayout, QHBoxLayout, QFileDialog, QPushButton, QLineEdit, QGroupBox

from pyqt_openai.apiData import getCompletionModel
from pyqt_openai.modelTable import ModelTable
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgLabel import SvgLabel


class LlamaPage(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initVal(self, db, ini_etc_dict, model_data):
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)

    def __initUi(self):
        pass