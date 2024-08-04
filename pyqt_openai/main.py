import os
import sys


# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

# for testing pyside6
os.environ['QT_API'] = 'pyside6'

# for testing pyqt6
# os.environ['QT_API'] = 'pyqt6'

from qtpy.QtGui import QGuiApplication, QFont, QIcon, QPixmap
from qtpy.QtWidgets import QApplication, \
    QSplashScreen
from qtpy.QtCore import Qt, QCoreApplication, QSettings
from qtpy.QtSql import QSqlDatabase

from pyqt_openai.mainWindow import MainWindow
from pyqt_openai.util.script import get_font, isUsingPyQt5
from pyqt_openai.sqlite import get_db_filename

from pyqt_openai import INI_FILE_NAME, APP_ICON

# HighDPI support
# Qt version should be above 5.14
if isUsingPyQt5():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)


# Application
class App(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.setQuitOnLastWindowClosed(False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.splash = QSplashScreen(QPixmap(APP_ICON))
        self.splash.show()

        self.__initGlobal()
        self.__initQSqlDb()
        self.__initFont()

        self.__showMainWindow()
        self.splash.finish(self.main_window)

    def __initQSqlDb(self):
        # Set up the database and table model (you'll need to configure this part based on your database)
        self.__imageDb = QSqlDatabase.addDatabase('QSQLITE')  # Replace with your database type
        self.__imageDb.setDatabaseName(get_db_filename())  # Replace with your database name
        self.__imageDb.open()

    def __initGlobal(self):
        """
        This function initializes the global variables including the settings file.
        """
        self.__settings_ini = QSettings(INI_FILE_NAME, QSettings.Format.IniFormat)
        self.show_as_markdown = self.__settings_ini.value('show_as_markdown', True, type=bool)

    def __initFont(self):
        font_dict = get_font()
        font_family = font_dict['font_family']
        font_size = font_dict['font_size']
        QApplication.setFont(QFont(font_family, font_size))

    def __showMainWindow(self):
        self.main_window = MainWindow()
        self.main_window.show()

def main():
    app = App(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()