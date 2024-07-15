import os
import sys
import webbrowser

import requests

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

# for testing pyside6
# os.environ['QT_API'] = 'pyside6'

# for testing pyqt6
# os.environ['QT_API'] = 'pyqt6'

from qtpy.QtGui import QGuiApplication, QFont, QIcon, QColor
from qtpy.QtWidgets import QMainWindow, QToolBar, QHBoxLayout, QDialog, QLineEdit, QPushButton, QWidgetAction, QSpinBox, QLabel, QWidget, QApplication, \
    QComboBox, QSizePolicy, QStackedWidget, QMenu, QSystemTrayIcon, \
    QMessageBox, QCheckBox, QAction
from qtpy.QtCore import Qt, QCoreApplication, QSettings
from qtpy.QtSql import QSqlDatabase

from pyqt_openai.models import SettingsParamsContainer
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.aboutDialog import AboutDialog
from pyqt_openai.customizeDialog import CustomizeDialog
from pyqt_openai.widgets.button import Button
from pyqt_openai.dalle_widget.dallEWidget import DallEWidget
from pyqt_openai.openAiChatBotWidget import OpenAIChatBotWidget
from pyqt_openai.replicate_widget.replicateWidget import ReplicateWidget
from pyqt_openai.settingsDialog import SettingsDialog
from pyqt_openai.util.script import get_db_filename
from pyqt_openai.doNotAskAgainDialog import DoNotAskAgainDialog

os.environ['OPENAI_API_KEY'] = ''

from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT, LLAMAINDEX_WRAPPER
from pyqt_openai.constants import PAYPAL_URL, BUYMEACOFFEE_URL

# HighDPI support
# qt version should be above 5.14
if os.environ['QT_API'] == 'pyqt5':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

QApplication.setFont(QFont('Arial', 12))
QApplication.setWindowIcon(QIcon('ico/openai.svg'))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)
        self.__settingsParamContainer = SettingsParamsContainer()
        self.__initSettings(self.__settingsParamContainer)

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['PyQt OpenAI Chatbot'])

        self.__openAiChatBotWidget = OpenAIChatBotWidget()
        self.__dallEWidget = DallEWidget()
        self.__replicateWidget = ReplicateWidget()

        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(self.__openAiChatBotWidget)
        self.__mainWidget.addWidget(self.__dallEWidget)
        self.__mainWidget.addWidget(self.__replicateWidget)

        self.__setActions()
        self.__setMenuBar()
        self.__setTrayMenu()
        self.__setToolBar()

        # load ini file
        self.__loadApiKeyInIni()

        # check if loaded API_KEY from ini file is not empty
        if os.environ['OPENAI_API_KEY']:
            self.__setApi()
        # if it is empty
        else:
            self.__setAIEnabled(False)
            self.__apiCheckPreviewLbl.hide()

        self.setCentralWidget(self.__mainWidget)
        self.resize(1280, 768)

        self.__refreshColumns()

    def __setActions(self):
        self.__langAction = QAction()

        # menu action
        self.__exitAction = QAction(LangClass.TRANSLATIONS['Exit'], self)
        self.__exitAction.triggered.connect(self.__beforeClose)

        self.__aboutAction = QAction(LangClass.TRANSLATIONS['About...'], self)
        self.__aboutAction.triggered.connect(self.__showAboutDialog)

        self.__paypalAction = QAction('Paypal', self)
        self.__paypalAction.triggered.connect(self.__paypal)

        self.__buyMeCoffeeAction = QAction('Buy me a coffee!', self)
        self.__buyMeCoffeeAction.triggered.connect(self.__buyMeCoffee)

        # toolbar action
        self.__chooseAiAction = QWidgetAction(self)
        self.__chooseAiCmbBox = QComboBox()
        self.__chooseAiCmbBox.addItems([LangClass.TRANSLATIONS['Chat'], LangClass.TRANSLATIONS['Image'], 'Replicate'])
        self.__chooseAiCmbBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.__chooseAiCmbBox.currentIndexChanged.connect(self.__aiTypeChanged)
        self.__chooseAiCmbBox.setMaximumWidth(100)
        self.__chooseAiAction.setDefaultWidget(self.__chooseAiCmbBox)

        self.__stackAction = QWidgetAction(self)
        self.__stackBtn = Button()
        self.__stackBtn.setStyleAndIcon('ico/stackontop.svg')
        self.__stackBtn.setCheckable(True)
        self.__stackBtn.toggled.connect(self.__stackToggle)
        self.__stackAction.setDefaultWidget(self.__stackBtn)
        self.__stackBtn.setToolTip(LangClass.TRANSLATIONS['Stack on Top'])

        self.__customizeAction = QWidgetAction(self)
        self.__customizeBtn = Button()
        self.__customizeBtn.setStyleAndIcon('ico/customize.svg')
        self.__customizeBtn.clicked.connect(self.__executeCustomizeDialog)
        self.__customizeAction.setDefaultWidget(self.__customizeBtn)
        self.__customizeBtn.setToolTip('Customize')

        self.__transparentAction = QWidgetAction(self)
        self.__transparentSpinBox = QSpinBox()
        self.__transparentSpinBox.setRange(20, 100)
        self.__transparentSpinBox.setValue(100)
        self.__transparentSpinBox.valueChanged.connect(self.__setTransparency)
        self.__transparentSpinBox.setToolTip(LangClass.TRANSLATIONS['Set Transparency of Window'])
        self.__transparentSpinBox.setMinimumWidth(100)

        self.__fullScreenAction = QWidgetAction(self)
        self.__fullScreenBtn = Button()
        self.__fullScreenBtn.setStyleAndIcon('ico/fullscreen.svg')
        self.__fullScreenBtn.setCheckable(True)
        self.__fullScreenBtn.toggled.connect(self.__fullScreenToggle)
        self.__fullScreenAction.setDefaultWidget(self.__fullScreenBtn)
        self.__fullScreenBtn.setToolTip('Full Screen')
        self.__fullScreenBtn.setShortcut('F11')

        lay = QHBoxLayout()
        lay.addWidget(self.__transparentSpinBox)

        transparencyActionWidget = QWidget()
        transparencyActionWidget.setLayout(lay)
        self.__transparentAction.setDefaultWidget(transparencyActionWidget)

        self.__showAiToolBarAction = QWidgetAction(self)
        self.__showAiToolBarChkBox = QCheckBox(LangClass.TRANSLATIONS['Show AI Toolbar'])
        self.__showAiToolBarChkBox.setChecked(self.__settingsParamContainer.show_secondary_toolbar)
        self.__showAiToolBarChkBox.toggled.connect(self.__showAiToolBarChkBoxChecked)
        self.__showAiToolBarAction.setDefaultWidget(self.__showAiToolBarChkBox)

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        apiLbl = QLabel('API')

        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText('Write your API Key...')
        self.__apiLineEdit.returnPressed.connect(self.__setApi)
        self.__apiLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        apiBtn = QPushButton(LangClass.TRANSLATIONS['Use'])
        apiBtn.clicked.connect(self.__setApi)

        lay = QHBoxLayout()
        lay.addWidget(apiLbl)
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(apiBtn)
        lay.addWidget(self.__apiCheckPreviewLbl)
        lay.setContentsMargins(0, 0, 0, 0)

        apiWidget = QWidget()
        apiWidget.setLayout(lay)

        self.__apiAction = QWidgetAction(self)
        self.__apiAction.setDefaultWidget(apiWidget)

        self.__settingsAction = QAction('Settings', self)
        self.__settingsAction.triggered.connect(self.__showSettingsDialog)

    def __fullScreenToggle(self, f):
        if f:
            self.showFullScreen()
        else:
            self.showNormal()

    def __lang_changed(self, lang):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(LangClass.TRANSLATIONS['Language Change'])
        msg_box.setText(LangClass.TRANSLATIONS['When changing the language, the program needs to be restarted. Would you like to restart it?'])
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.__settings_struct.setValue('lang', lang)
            # save the changes to the file
            self.__settings_struct.sync()
            # Define the arguments to be passed to the executable
            args = [sys.executable, "main.py"]
            # Call os.execv() to execute the new process
            os.execv(sys.executable, args)

    def __setMenuBar(self):
        menubar = self.menuBar()

        # create the "File" menu
        fileMenu = QMenu(LangClass.TRANSLATIONS['File'], self)
        fileMenu.addAction(self.__settingsAction)
        fileMenu.addAction(self.__exitAction)
        menubar.addMenu(fileMenu)

        # create the "Help" menu
        helpMenu = QMenu(LangClass.TRANSLATIONS['Help'], self)
        menubar.addMenu(helpMenu)

        helpMenu.addAction(self.__aboutAction)

        donateMenu = QMenu('Donate', self)
        donateMenu.addAction(self.__paypalAction)
        donateMenu.addAction(self.__buyMeCoffeeAction)

        menubar.addMenu(donateMenu)

    def __setTrayMenu(self):
        # background app
        menu = QMenu()

        action = QAction("Quit", self)
        action.setIcon(QIcon('ico/close.svg'))

        action.triggered.connect(app.quit)

        menu.addAction(action)

        tray_icon = QSystemTrayIcon(app)
        tray_icon.setIcon(QIcon('ico/openai.svg'))
        tray_icon.activated.connect(self.__activated)

        tray_icon.setContextMenu(menu)

        tray_icon.show()

    def __activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def __setToolBar(self):
        self.__toolbar = QToolBar()
        lay = self.__toolbar.layout()
        self.__toolbar.addAction(self.__chooseAiAction)
        self.__toolbar.addAction(self.__stackAction)
        self.__toolbar.addAction(self.__customizeAction)
        self.__toolbar.addAction(self.__fullScreenAction)
        self.__toolbar.addAction(self.__transparentAction)
        self.__toolbar.addAction(self.__showAiToolBarAction)
        self.__toolbar.addAction(self.__apiAction)
        self.__toolbar.setLayout(lay)
        self.__toolbar.setMovable(False)

        self.addToolBar(self.__toolbar)

        # QToolbar's layout can't be set spacing with lay.setSpacing so i've just did this instead
        self.__toolbar.setStyleSheet('QToolBar { spacing: 2px; }')

        self.__toolbar.setVisible(self.__settingsParamContainer.show_toolbar)
        for i in range(self.__mainWidget.count()):
            currentWidget = self.__mainWidget.widget(i)
            currentWidget.showSecondaryToolBar(self.__settingsParamContainer.show_secondary_toolbar)
        self.__mainWidget.currentWidget().showThreadToolWidget(self.__settingsParamContainer.thread_tool_widget)

    def __setApiKeyAndClient(self, api_key):
        # for subprocess (mostly)
        os.environ['OPENAI_API_KEY'] = api_key
        # for showing to the user
        self.__apiLineEdit.setText(api_key)

        OPENAI_STRUCT.api_key = os.environ['OPENAI_API_KEY']

    def __loadApiKeyInIni(self):
        # this api key should be yours
        if self.__settings_struct.contains('API_KEY'):
            self.__setApiKeyAndClient(self.__settings_struct.value('API_KEY'))
        else:
            self.__settings_struct.setValue('API_KEY', '')

        # Set llama index directory if it exists
        if self.__settings_struct.contains('llama_index_directory'):
            LLAMAINDEX_WRAPPER.set_directory(self.__settings_struct.value('llama_index_directory'))

    def __setAIEnabled(self, f):
        self.__openAiChatBotWidget.setAIEnabled(f)
        self.__dallEWidget.setAIEnabled(f)

    def __setApi(self):
        try:
            api_key = self.__apiLineEdit.text()
            response = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {api_key}'})
            f = response.status_code == 200
            self.__setAIEnabled(f)
            if f:
                self.__setApiKeyAndClient(api_key)
                self.__settings_struct.setValue('API_KEY', api_key)

                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(0, 200, 0).name()))
                self.__apiCheckPreviewLbl.setText(LangClass.TRANSLATIONS['API key is valid'])
            else:
                raise Exception
        except Exception as e:
            self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(255, 0, 0).name()))
            self.__apiCheckPreviewLbl.setText(LangClass.TRANSLATIONS['API key is invalid'])
            self.__setAIEnabled(False)
            print(e)
        finally:
            self.__apiCheckPreviewLbl.show()

    def __showAboutDialog(self):
        aboutDialog = AboutDialog()
        aboutDialog.exec()

    def __paypal(self):
        webbrowser.open(PAYPAL_URL)

    def __buyMeCoffee(self):
        webbrowser.open(BUYMEACOFFEE_URL)

    def __stackToggle(self, f):
        if f:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def __setTransparency(self, v):
        self.setWindowOpacity(v / 100)

    def __showAiToolBarChkBoxChecked(self, f):
        self.__mainWidget.currentWidget().showSecondaryToolBar(f)
        self.__settingsParamContainer.show_secondary_toolbar = f

    def __executeCustomizeDialog(self):
        dialog = CustomizeDialog(self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self.__openAiChatBotWidget.refreshCustomizedInformation()

    def __aiTypeChanged(self, i):
        self.__mainWidget.setCurrentIndex(i)
        widget = self.__mainWidget.currentWidget()
        widget.showSecondaryToolBar(self.__settingsParamContainer.show_secondary_toolbar)

    def __initSettings(self, container):
        self.__settingsParamContainer = container
        for k, v in container.get_items():
            if not self.__settings_struct.contains(k):
                self.__settings_struct.setValue(k, v)
            else:
                setattr(container, k, self.__settings_struct.value(k, type=type(v)))
        self.__lang = LangClass.lang_changed(self.__settingsParamContainer.lang)

    def __refreshSettings(self, container):
        self.__settingsParamContainer = container
        # If db name is changed
        if self.__settingsParamContainer.db != self.__settings_struct.value('db'):
            QMessageBox.information(self, 'Info', "The name of the reference target database has been changed. The changes will take effect after a restart.")
        # If show_toolbar is changed
        if self.__settingsParamContainer.show_toolbar != self.__settings_struct.value('show_toolbar'):
            self.__toolbar.setVisible(self.__settingsParamContainer.show_toolbar)
        # If show_secondary_toolbar is changed
        if self.__settingsParamContainer.show_secondary_toolbar != self.__settings_struct.value('show_secondary_toolbar'):
            for i in range(self.__mainWidget.count()):
                currentWidget = self.__mainWidget.widget(i)
                currentWidget.showSecondaryToolBar(self.__settingsParamContainer.show_secondary_toolbar)
        # If thread_tool_widget is changed
        if self.__settingsParamContainer.thread_tool_widget != self.__settings_struct.value('thread_tool_widget'):
            if isinstance(self.__mainWidget.currentWidget(), OpenAIChatBotWidget):
                self.__mainWidget.currentWidget().showThreadToolWidget(self.__settingsParamContainer.thread_tool_widget)
        for k, v in container.get_items():
            self.__settings_struct.setValue(k, v)
        # If language is changed
        if self.__settingsParamContainer.lang != self.__lang:
            self.__lang = LangClass.lang_changed(self.__settingsParamContainer.lang)
            self.__lang_changed(self.__settingsParamContainer.lang)
        self.__refreshColumns()

    def __refreshColumns(self):
        self.__openAiChatBotWidget.setColumns(self.__settingsParamContainer.chat_column_to_show)
        self.__dallEWidget.setColumns(self.__settingsParamContainer.image_column_to_show)
        self.__replicateWidget.setColumns(self.__settingsParamContainer.image_column_to_show)

    def __showSettingsDialog(self):
        dialog = SettingsDialog(self.__settingsParamContainer)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            self.__refreshSettings(dialog.getSettingsParam())

    def __doNotAskAgainChanged(self, value):
        self.__settingsParamContainer.do_not_ask_again = value
        self.__refreshSettings(self.__settingsParamContainer)

    def __beforeClose(self):
        if self.__settingsParamContainer.do_not_ask_again:
            app = QApplication.instance()
            app.quit()
        else:
            # Show a message box to confirm the exit or cancel or running in the background
            dialog = DoNotAskAgainDialog(self.__settingsParamContainer.do_not_ask_again)
            dialog.doNotAskAgainChanged.connect(self.__doNotAskAgainChanged)
            reply = dialog.exec()
            if dialog.isCancel():
                return True
            else:
                if reply == QDialog.DialogCode.Accepted:
                    app = QApplication.instance()
                    app.quit()
                elif reply == QDialog.DialogCode.Rejected:
                    self.close()

    def closeEvent(self, e):
        f = self.__beforeClose()
        if f:
            e.ignore()
        else:
            return super().closeEvent(e)


# Application
class App(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.setQuitOnLastWindowClosed(False)
        self.__initQSqlDb()

    def __initQSqlDb(self):
        # Set up the database and table model (you'll need to configure this part based on your database)
        self.__imageDb = QSqlDatabase.addDatabase('QSQLITE')  # Replace with your database type
        self.__imageDb.setDatabaseName(get_db_filename())  # Replace with your database name
        self.__imageDb.open()


if __name__ == "__main__":
    import sys

    app = App(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())