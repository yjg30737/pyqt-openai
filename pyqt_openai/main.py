from __future__ import annotations

import os
import sys

# Get the absolute path of the current script file

if __name__ == "__main__":
    script_path: str = os.path.abspath(__file__)

    # Get the root directory by going up one level from the script directory
    project_root: str = os.path.dirname(os.path.dirname(script_path))

    sys.path.insert(0, project_root)
    sys.path.insert(0, os.getcwd())  # Add the current directory as well

# for testing pyside6
# os.environ['QT_API'] = 'pyside6'

# for testing pyqt6
# os.environ['QT_API'] = 'pyqt6'

from qtpy.QtGui import QFont, QIcon, QPixmap
from qtpy.QtSql import QSqlDatabase
from qtpy.QtWidgets import QApplication, QSplashScreen

from pyqt_openai import DEFAULT_APP_ICON
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.mainWindow import MainWindow
from pyqt_openai.sqlite import get_db_filename
from pyqt_openai.updateSoftwareDialog import update_software
from pyqt_openai.util.common import handle_exception


# Application
class App(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.setQuitOnLastWindowClosed(False)
        self.setWindowIcon(QIcon(DEFAULT_APP_ICON))
        self.splash: QSplashScreen = QSplashScreen(QPixmap(DEFAULT_APP_ICON))
        self.splash.show()

        self.__initQSqlDb()
        self.__initFont()

        self.__showMainWindow()
        self.splash.finish(self.main_window)

        update_software()

    def __initQSqlDb(self):
        # Set up the database and table model (you'll need to configure this part based on your database)
        self.__db: QSqlDatabase = QSqlDatabase.addDatabase("QSQLITE")
        self.__db.setDatabaseName(get_db_filename())
        self.__db.open()

    def __initFont(self):
        font_family: str = CONFIG_MANAGER.get_general_property("font_family") or "Arial"
        font_size: int = int(CONFIG_MANAGER.get_general_property("font_size") or 12)
        QApplication.setFont(QFont(font_family, font_size))

    def __showMainWindow(self):
        self.main_window: MainWindow = MainWindow()
        self.main_window.show()


# Set the global exception handler
sys.excepthook = handle_exception


def main():
    app: App = App(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
