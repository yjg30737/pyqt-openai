import time

import os, sys
import openai, requests

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtGui import QGuiApplication, QFont, QIcon, QColor
from qtpy.QtWidgets import QMainWindow, QToolBar, QHBoxLayout, QDialog, QLineEdit, QPushButton, QWidgetAction, QSpinBox, QLabel, QWidget, QApplication, \
    QComboBox, QSizePolicy, QStackedWidget, QAction, QMenu, QSystemTrayIcon, \
    QMessageBox, QCheckBox
from qtpy.QtCore import Qt, QCoreApplication, QSettings

from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.aboutDialog import AboutDialog
from pyqt_openai.customizeDialog import CustomizeDialog
from pyqt_openai.svgButton import SvgButton
from pyqt_openai.image_gen_widget.imageGeneratingToolWidget import ImageGeneratingToolWidget
from pyqt_openai.openAiChatBotWidget import OpenAIChatBotWidget

# for testing pyside6
# if you use pyside6 already, you don't have to remove the #
# os.environ['QT_API'] = 'pyside6'

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support
# qt version should be above 5.14
# todo check the qt version with qtpy
if os.environ['QT_API'] == 'pyqt5' or os.environ['QT_API'] != 'pyside6':
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

QApplication.setFont(QFont('Arial', 12))
QApplication.setWindowIcon(QIcon('ico/openai.svg'))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)
        self.__lang = None
        if not self.__settings_struct.contains('lang'):
            self.__settings_struct.setValue('lang', LangClass.lang_changed())
        else:
            self.__lang = self.__settings_struct.value('lang', type=str)
        self.__lang = LangClass.lang_changed(self.__lang)

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['PyQt OpenAI Chatbot'])

        self.__openAiChatBotWidget = OpenAIChatBotWidget()
        self.__openAiChatBotWidget.notifierWidgetActivated.connect(self.show)
        self.__imageGeneratingToolWidget = ImageGeneratingToolWidget()
        self.__imageGeneratingToolWidget.notifierWidgetActivated.connect(self.show)
        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(self.__openAiChatBotWidget)
        self.__mainWidget.addWidget(self.__imageGeneratingToolWidget)

        self.__setActions()
        self.__setMenuBar()
        self.__setTrayMenu()
        self.__setToolBar()

        # load ini file
        self.__loadApiKeyInIni()

        # check if loaded API_KEY from ini file is not empty
        if openai.api_key:
            self.__setApi()
        # if it is empty
        else:
            self.__setAIEnabled(False)
            self.__apiCheckPreviewLbl.hide()

        self.setCentralWidget(self.__mainWidget)
        self.resize(1024, 768)

    def __setActions(self):
        # menu action
        self.__exitAction = QAction(LangClass.TRANSLATIONS['Exit'], self)
        self.__exitAction.triggered.connect(self.close)

        self.__aboutAction = QAction(LangClass.TRANSLATIONS['About...'], self)
        self.__aboutAction.triggered.connect(self.__showAboutDialog)

        # toolbar action
        self.__chooseAiAction = QWidgetAction(self)
        self.__chooseAiCmbBox = QComboBox()
        self.__chooseAiCmbBox.addItems([LangClass.TRANSLATIONS['Chat'], LangClass.TRANSLATIONS['Image']])
        self.__chooseAiCmbBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__chooseAiCmbBox.currentIndexChanged.connect(self.__aiTypeChanged)
        self.__chooseAiAction.setDefaultWidget(self.__chooseAiCmbBox)

        self.__stackAction = QWidgetAction(self)
        self.__stackBtn = SvgButton()
        self.__stackBtn.setIcon('ico/stackontop.svg')
        self.__stackBtn.setCheckable(True)
        self.__stackBtn.toggled.connect(self.__stackToggle)
        self.__stackAction.setDefaultWidget(self.__stackBtn)
        self.__stackBtn.setToolTip(LangClass.TRANSLATIONS['Stack on Top'])

        self.__customizeAction = QWidgetAction(self)
        self.__customizeBtn = SvgButton()
        self.__customizeBtn.setIcon('ico/customize.svg')
        self.__customizeBtn.clicked.connect(self.__executeCustomizeDialog)
        self.__customizeAction.setDefaultWidget(self.__customizeBtn)
        self.__customizeBtn.setToolTip(LangClass.TRANSLATIONS['Customize (working)'])

        self.__transparentAction = QWidgetAction(self)
        self.__transparentSpinBox = QSpinBox()
        self.__transparentSpinBox.setRange(0, 100)
        self.__transparentSpinBox.setValue(100)
        self.__transparentSpinBox.valueChanged.connect(self.__setTransparency)
        self.__transparentSpinBox.setToolTip(LangClass.TRANSLATIONS['Set Transparency of Window'])

        lay = QHBoxLayout()
        lay.addWidget(QLabel(LangClass.TRANSLATIONS['Window Transparency']))
        lay.addWidget(self.__transparentSpinBox)

        transparencyActionWidget = QWidget()
        transparencyActionWidget.setLayout(lay)
        self.__transparentAction.setDefaultWidget(transparencyActionWidget)

        self.__showAiToolBarAction = QWidgetAction(self)
        self.__showAiToolBarChkBox = QCheckBox(LangClass.TRANSLATIONS['Show AI Toolbar'])
        self.__showAiToolBarChkBox.setChecked(True)
        self.__showAiToolBarChkBox.toggled.connect(self.__showAiToolBarChkBoxChecked)
        self.__showAiToolBarAction.setDefaultWidget(self.__showAiToolBarChkBox)

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        apiLbl = QLabel('API')

        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText('Write your API Key...')
        self.__apiLineEdit.returnPressed.connect(self.__setApi)
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)

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

        self.__langAction = QWidgetAction(self)
        self.__langCmbBox = QComboBox()
        self.__langCmbBox.addItems(list(LangClass.LANGUAGE_DICT.keys()))
        self.__langCmbBox.setCurrentText(self.__lang)
        self.__langCmbBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__langCmbBox.currentTextChanged.connect(self.__lang_changed)
        self.__langAction.setDefaultWidget(self.__langCmbBox)

    def __lang_changed(self, lang):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(LangClass.TRANSLATIONS['Language Change'])
        msg_box.setText(LangClass.TRANSLATIONS['When changing the language, the program needs to be restarted. Would you like to restart it?'])
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)

        # 메시지 상자 표시 및 사용자 입력 처리
        result = msg_box.exec_()

        if result == QMessageBox.Yes:
            self.__settings_struct.setValue('lang', lang)
            # save the changes to the file
            self.__settings_struct.sync()
            # Define the arguments to be passed to the executable
            args = [sys.executable, "main.py"]
            # Call os.execv() to execute the new process
            os.execv(sys.executable, args)
        else:
            self.__langCmbBox.currentTextChanged.disconnect(self.__lang_changed)
            self.__langCmbBox.setCurrentText(self.__lang)
            self.__langCmbBox.currentTextChanged.connect(self.__lang_changed)

    def __setMenuBar(self):
        menubar = self.menuBar()

        # create the "File" menu
        fileMenu = QMenu(LangClass.TRANSLATIONS['File'], self)
        fileMenu.addAction(self.__exitAction)
        menubar.addMenu(fileMenu)

        # create the "Help" menu
        helpMenu = QMenu(LangClass.TRANSLATIONS['Help'], self)
        menubar.addMenu(helpMenu)

        helpMenu.addAction(self.__aboutAction)

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
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def __setToolBar(self):
        aiTypeToolBar = QToolBar()
        aiTypeToolBar.setMovable(False)
        aiTypeToolBar.addAction(self.__chooseAiAction)

        langToolBar = QToolBar()
        langToolBar.setMovable(False)
        langToolBar.addAction(self.__langAction)

        windowToolBar = QToolBar()
        lay = windowToolBar.layout()
        windowToolBar.addAction(self.__stackAction)
        windowToolBar.addAction(self.__customizeAction)
        windowToolBar.addAction(self.__transparentAction)
        windowToolBar.addAction(self.__showAiToolBarAction)
        windowToolBar.addAction(self.__apiAction)
        windowToolBar.setLayout(lay)
        windowToolBar.setMovable(False)

        self.addToolBar(aiTypeToolBar)
        self.addToolBar(langToolBar)
        self.addToolBar(windowToolBar)

        # QToolbar's layout can't be set spacing with lay.setSpacing so i've just did this instead
        windowToolBar.setStyleSheet('QToolBar { spacing: 2px; }')

    def __setApiKey(self, api_key):
        # for script
        openai.api_key = api_key
        # for subprocess (mostly)
        os.environ['OPENAI_API_KEY'] = api_key
        # for showing to the user
        self.__apiLineEdit.setText(api_key)

    def __loadApiKeyInIni(self):
        # this api key should be yours
        if self.__settings_struct.contains('API_KEY'):
            self.__setApiKey(self.__settings_struct.value('API_KEY'))
        else:
            self.__settings_struct.setValue('API_KEY', '')

    def __setAIEnabled(self, f):
        self.__openAiChatBotWidget.setAIEnabled(f)
        self.__imageGeneratingToolWidget.setAIEnabled(f)

    def __setApi(self):
        try:
            api_key = self.__apiLineEdit.text()
            response = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {api_key}'})
            f = response.status_code == 200
            self.__setAIEnabled(f)
            if f:
                self.__setApiKey(api_key)
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

    def __stackToggle(self, f):
        if f:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def __setTransparency(self, v):
        self.setWindowOpacity(v / 100)

    def __showAiToolBarChkBoxChecked(self, f):
        self.__mainWidget.currentWidget().showAiToolBar(f)

    def __executeCustomizeDialog(self):
        dialog = CustomizeDialog(self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            pass

    def __aiTypeChanged(self, i):
        self.__mainWidget.setCurrentIndex(i)

    def closeEvent(self, e):
        message = LangClass.TRANSLATIONS['The window will be closed. Would you like to continue running this app in the background?']
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle(LangClass.TRANSLATIONS['Wait!'])
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = closeMessageBox.exec()
        # Yes
        if reply == 16384:
            e.accept()
        # No
        elif reply == 65536:
            app.quit()
        return super().closeEvent(e)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())