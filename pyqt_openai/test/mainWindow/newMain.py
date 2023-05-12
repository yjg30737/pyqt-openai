import os, json, webbrowser, openai

import requests
from PyQt5.QtGui import QGuiApplication, QFont, QIcon, QColor, QCursor
from PyQt5.QtWidgets import QMainWindow, QToolBar, QHBoxLayout, QWidgetAction, QSpinBox, QLabel, QWidget, QApplication, \
    QPushButton, QComboBox, QSizePolicy, QStackedWidget, QAction, QMenu, QVBoxLayout, QFrame, QSystemTrayIcon, \
    QMessageBox, QSplitter, QListWidgetItem, QFileDialog, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt, QSettings, QEvent, QCoreApplication

from pyqt_openai.apiData import ModelData
from pyqt_openai.chatWidget import Prompt, ChatBrowser
from pyqt_openai.clickableTooltip import ClickableTooltip
from pyqt_openai.leftSideBar import LeftSideBar
from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.openAiThread import OpenAIThread
from pyqt_openai.prompt.promptGeneratorWidget import PromptGeneratorWidget
from pyqt_openai.right_sidebar.aiPlaygroundWidget import AIPlaygroundWidget
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgButton import SvgButton
from pyqt_openai.test.mainWindow.image_gen_widget.imageGeneratingToolWidget import ImageGeneratingToolWidget
from pyqt_openai.test.mainWindow.openAiChatBotWidget import OpenAIChatBotWidget

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

QApplication.setFont(QFont('Arial', 12))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('PyQt OpenAI Chatbot')
        self.setWindowIcon(QIcon('../../ico/openai.svg'))

        self.__openAiChatBotWidget = OpenAIChatBotWidget()
        self.__imageGeneratingToolWidget = ImageGeneratingToolWidget()
        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(self.__openAiChatBotWidget)
        self.__mainWidget.addWidget(self.__imageGeneratingToolWidget)

        self.__setActions()
        self.__setMenuBar()
        self.__setTrayMenu()
        self.__setToolBar()

        self.setCentralWidget(self.__mainWidget)
        self.resize(1024, 768)

    def __setActions(self):
        # menu action
        self.__exitAction = QAction("Exit", self)
        self.__exitAction.triggered.connect(self.close)

        self.__aboutAction = QAction("About...", self)
        self.__aboutAction.triggered.connect(self.__showAboutDialog)

        # toolbar action
        self.__chooseAiAction = QWidgetAction(self)
        self.__chooseAiCmbBox = QComboBox()
        self.__chooseAiCmbBox.addItems(['Chat', 'Image'])
        self.__chooseAiCmbBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__chooseAiCmbBox.currentIndexChanged.connect(self.__aiTypeChanged)
        self.__chooseAiAction.setDefaultWidget(self.__chooseAiCmbBox)

        self.__stackAction = QWidgetAction(self)
        self.__stackBtn = SvgButton()
        self.__stackBtn.setIcon('ico/stackontop.svg')
        self.__stackBtn.setCheckable(True)
        self.__stackBtn.toggled.connect(self.__stackToggle)
        self.__stackAction.setDefaultWidget(self.__stackBtn)
        self.__stackBtn.setToolTip('Always On Top')

        self.__customizeAction = QWidgetAction(self)
        self.__customizeBtn = SvgButton()
        self.__customizeBtn.setIcon('ico/customize.svg')
        self.__customizeBtn.clicked.connect(self.__executeCustomizeDialog)
        self.__customizeAction.setDefaultWidget(self.__customizeBtn)
        self.__customizeBtn.setToolTip('Customize (working)')

        self.__transparentAction = QWidgetAction(self)
        self.__transparentSpinBox = QSpinBox()
        self.__transparentSpinBox.setRange(0, 100)
        self.__transparentSpinBox.setValue(100)
        self.__transparentSpinBox.valueChanged.connect(self.__setTransparency)
        self.__transparentSpinBox.setToolTip('Set Transparency of Window')

        lay = QHBoxLayout()
        lay.addWidget(QLabel('Window Transparency'))
        lay.addWidget(self.__transparentSpinBox)

        transparencyActionWidget = QWidget()
        transparencyActionWidget.setLayout(lay)
        self.__transparentAction.setDefaultWidget(transparencyActionWidget)

        self.__showAiToolBarAction = QWidgetAction(self)
        self.__showAiToolBarChkBox = QCheckBox('Show AI Toolbar')
        self.__showAiToolBarChkBox.setChecked(True)
        self.__showAiToolBarChkBox.toggled.connect(self.__showAiToolBarChkBoxChecked)
        self.__showAiToolBarAction.setDefaultWidget(self.__showAiToolBarChkBox)

    def __setMenuBar(self):
        menubar = self.menuBar()

        # create the "File" menu
        fileMenu = QMenu("File", self)
        fileMenu.addAction(self.__exitAction)
        menubar.addMenu(fileMenu)

        # create the "Help" menu
        helpMenu = QMenu("Help", self)
        menubar.addMenu(helpMenu)

        helpMenu.addAction(self.__aboutAction)

    def __setTrayMenu(self):
        # background app
        menu = QMenu()

        action = QAction("Quit", self)
        action.setIcon(QIcon('../../ico/close.svg'))

        action.triggered.connect(app.quit)

        menu.addAction(action)

        tray_icon = QSystemTrayIcon(app)
        tray_icon.setIcon(QIcon('../../ico/openai.svg'))
        tray_icon.activated.connect(self.__activated)

        tray_icon.setContextMenu(menu)

        tray_icon.show()

    def __activated(self, reason):
        if reason == 3:
            self.show()

    def __setToolBar(self):
        aiTypeToolBar = QToolBar()
        aiTypeToolBar.setMovable(False)
        aiTypeToolBar.addAction(self.__chooseAiAction)

        windowToolBar = QToolBar()
        lay = QHBoxLayout()
        windowToolBar.addAction(self.__stackAction)
        windowToolBar.addAction(self.__customizeAction)
        windowToolBar.addAction(self.__transparentAction)
        windowToolBar.addAction(self.__showAiToolBarAction)
        windowToolBar.setLayout(lay)
        windowToolBar.setMovable(False)
        self.addToolBar(aiTypeToolBar)
        self.addToolBar(windowToolBar)
        # QToolbar's layout can't be set spacing with lay.setSpacing so i've just did this instead
        windowToolBar.setStyleSheet('QToolBar { spacing: 2px; }')

    def __showAboutDialog(self):
        print('__showAboutDialog')

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
        pass

    def __aiTypeChanged(self, i):
        self.__mainWidget.setCurrentIndex(i)

    def closeEvent(self, e):
        message = 'The window has been closed. Would you like to continue running this app in the background?'
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle('Wait!')
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