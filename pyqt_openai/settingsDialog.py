import os, sys

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtCore import Qt, QRegularExpression
from qtpy.QtGui import QIcon, QRegularExpressionValidator
from qtpy.QtWidgets import QDialog, QComboBox, QLineEdit, QCheckBox, QSizePolicy, \
    QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox, QWidget, QMessageBox


from pyqt_openai import constants
from pyqt_openai.models import SettingsParamsContainer
from pyqt_openai.res.language_dict import LangClass


class SettingsDialog(QDialog):
    def __init__(self, args: SettingsParamsContainer, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.__initVal(args)
        self.__initUi()

    def __initVal(self, args):
        self.__lang = args.lang
        self.__db = args.db
        self.__do_not_ask_again = args.do_not_ask_again
        self.__notify_finish = args.notify_finish
        self.__show_toolbar = args.show_toolbar

    def __initUi(self):
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("ico/setting.svg"))
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)

        # Language setting
        self.__langCmbBox = QComboBox()
        self.__langCmbBox.addItems(list(LangClass.LANGUAGE_DICT.keys()))
        self.__langCmbBox.setCurrentText(self.__lang)
        self.__langCmbBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        lay = QHBoxLayout()
        lay.addWidget(QLabel("Language:"))
        lay.addWidget(self.__langCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        langWidget = QWidget()
        langWidget.setLayout(lay)

        # Database setting
        dbLayout = QHBoxLayout()
        self.__dbLineEdit = QLineEdit(self.__db)
        self.__validator = QRegularExpressionValidator()
        re = QRegularExpression(constants.DB_NAME_REGEX)
        self.__validator.setRegularExpression(re)
        self.__dbLineEdit.setValidator(self.__validator)

        dbLayout.addWidget(QLabel("Database Path:"))
        dbLayout.addWidget(self.__dbLineEdit)

        # Checkboxes
        self.__doNotAskAgainCheckBox = QCheckBox("Do not ask again when closing (Always close the application)")
        self.__doNotAskAgainCheckBox.setChecked(self.__do_not_ask_again)
        self.__notifyFinishCheckBox = QCheckBox("Notify when finish processing any task (Conversion, etc.)")
        self.__notifyFinishCheckBox.setChecked(self.__notify_finish)
        self.__showToolbarCheckBox = QCheckBox("Show toolbar")
        self.__showToolbarCheckBox.setChecked(self.__show_toolbar)

        # Dialog buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.__accept)
        buttonBox.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addWidget(langWidget)
        lay.addLayout(dbLayout)
        lay.addWidget(self.__doNotAskAgainCheckBox)
        lay.addWidget(self.__notifyFinishCheckBox)
        lay.addWidget(self.__showToolbarCheckBox)
        lay.addWidget(buttonBox)

        self.setLayout(lay)

    def __accept(self):
        # If DB file name is empty
        if self.__dbLineEdit.text().strip() == '':
            QMessageBox.critical(self, 'No.', 'DB filename is empty. Please write something!')
        else:
            self.accept()

    def getSettingsParam(self):
        return SettingsParamsContainer(
            lang=self.__langCmbBox.currentText(),
            db=self.__dbLineEdit.text(),
            do_not_ask_again=self.__doNotAskAgainCheckBox.isChecked(),
            notify_finish=self.__notifyFinishCheckBox.isChecked(),
            show_toolbar=self.__showToolbarCheckBox.isChecked()
        )



if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    param = SettingsParamsContainer()
    dialog = SettingsDialog(param)
    dialog.show()
    sys.exit(app.exec_())