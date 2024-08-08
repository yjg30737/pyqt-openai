import os

import requests
from qtpy.QtCore import Qt, QSettings
from qtpy.QtGui import QFont, QIcon, QColor
from qtpy.QtWidgets import QMainWindow, QToolBar, QHBoxLayout, QDialog, QLineEdit, QPushButton, QWidgetAction, QSpinBox, \
    QLabel, QWidget, QApplication, \
    QComboBox, QSizePolicy, QStackedWidget, QMenu, QSystemTrayIcon, \
    QMessageBox, QCheckBox, QAction

from pyqt_openai.config_loader import CONFIG_MANAGER

from pyqt_openai import INI_FILE_NAME, DEFAULT_SHORTCUT_FULL_SCREEN, \
    APP_INITIAL_WINDOW_SIZE, DEFAULT_APP_NAME, DEFAULT_APP_ICON, ICON_STACKONTOP, ICON_CUSTOMIZE, ICON_FULLSCREEN, ICON_CLOSE, \
    DEFAULT_SHORTCUT_SETTING, TRANSPARENT_RANGE, TRANSPARENT_INIT_VAL
from pyqt_openai.aboutDialog import AboutDialog
from pyqt_openai.gpt_widget.gptMainWidget import GPTMainWidget
from pyqt_openai.customizeDialog import CustomizeDialog
from pyqt_openai.dalle_widget.dalleMainWidget import DallEMainWidget
from pyqt_openai.doNotAskAgainDialog import DoNotAskAgainDialog
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import SettingsParamsContainer, CustomizeParamsContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT, init_llama
from pyqt_openai.replicate_widget.replicateMainWidget import ReplicateMainWidget
from pyqt_openai.settingsDialog import SettingsDialog
from pyqt_openai.util.script import restart_app, show_message_box_after_change_to_restart, goPayPal, goBuyMeCoffee
from pyqt_openai.widgets.button import Button


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settingsParamContainer = SettingsParamsContainer()
        self.__customizeParamsContainer = CustomizeParamsContainer()

        self.__initContainer(self.__settingsParamContainer)
        self.__initContainer(self.__customizeParamsContainer)

    def __initUi(self):
        self.setWindowTitle(DEFAULT_APP_NAME)

        self.__gptWidget = GPTMainWidget(self)
        self.__dallEWidget = DallEMainWidget(self)
        self.__replicateWidget = ReplicateMainWidget(self)

        self.__mainWidget = QStackedWidget()
        self.__mainWidget.addWidget(self.__gptWidget)
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
        self.resize(*APP_INITIAL_WINDOW_SIZE)

        self.__refreshColumns()
        self.__gptWidget.refreshCustomizedInformation(self.__customizeParamsContainer)

    def __setActions(self):
        self.__langAction = QAction()

        # menu action
        self.__exitAction = QAction(LangClass.TRANSLATIONS['Exit'], self)
        self.__exitAction.triggered.connect(self.__beforeClose)

        self.__aboutAction = QAction(LangClass.TRANSLATIONS['About...'], self)
        self.__aboutAction.triggered.connect(self.__showAboutDialog)

        self.__paypalAction = QAction('Paypal', self)
        self.__paypalAction.triggered.connect(goPayPal)

        self.__buyMeCoffeeAction = QAction('Buy me a coffee!', self)
        self.__buyMeCoffeeAction.triggered.connect(goBuyMeCoffee)

        # toolbar action
        self.__chooseAiAction = QWidgetAction(self)
        self.__chooseAiCmbBox = QComboBox()
        self.__chooseAiCmbBox.addItems([LangClass.TRANSLATIONS['Chat'], LangClass.TRANSLATIONS['Image'], 'Replicate'])
        self.__chooseAiCmbBox.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.__chooseAiCmbBox.currentIndexChanged.connect(self.__aiTypeChanged)
        self.__chooseAiAction.setDefaultWidget(self.__chooseAiCmbBox)

        self.__stackAction = QWidgetAction(self)
        self.__stackBtn = Button()
        self.__stackBtn.setStyleAndIcon(ICON_STACKONTOP)
        self.__stackBtn.setCheckable(True)
        self.__stackBtn.toggled.connect(self.__stackToggle)
        self.__stackAction.setDefaultWidget(self.__stackBtn)
        self.__stackBtn.setToolTip(LangClass.TRANSLATIONS['Stack on Top'])

        self.__customizeAction = QWidgetAction(self)
        self.__customizeBtn = Button()
        self.__customizeBtn.setStyleAndIcon(ICON_CUSTOMIZE)
        self.__customizeBtn.clicked.connect(self.__executeCustomizeDialog)
        self.__customizeAction.setDefaultWidget(self.__customizeBtn)
        self.__customizeBtn.setToolTip(LangClass.TRANSLATIONS['Customize'])

        self.__transparentAction = QWidgetAction(self)
        self.__transparentSpinBox = QSpinBox()
        self.__transparentSpinBox.setRange(*TRANSPARENT_RANGE)
        self.__transparentSpinBox.setValue(TRANSPARENT_INIT_VAL)
        self.__transparentSpinBox.valueChanged.connect(self.__setTransparency)
        self.__transparentSpinBox.setToolTip(LangClass.TRANSLATIONS['Set Transparency of Window'])
        self.__transparentSpinBox.setMinimumWidth(100)

        self.__fullScreenAction = QWidgetAction(self)
        self.__fullScreenBtn = Button()
        self.__fullScreenBtn.setStyleAndIcon(ICON_FULLSCREEN)
        self.__fullScreenBtn.setCheckable(True)
        self.__fullScreenBtn.toggled.connect(self.__fullScreenToggle)
        self.__fullScreenAction.setDefaultWidget(self.__fullScreenBtn)
        self.__fullScreenBtn.setToolTip(LangClass.TRANSLATIONS['Full Screen'] + f' ({DEFAULT_SHORTCUT_FULL_SCREEN})')
        self.__fullScreenBtn.setShortcut(DEFAULT_SHORTCUT_FULL_SCREEN)

        lay = QHBoxLayout()
        lay.addWidget(self.__transparentSpinBox)

        transparencyActionWidget = QWidget(self)
        transparencyActionWidget.setLayout(lay)
        self.__transparentAction.setDefaultWidget(transparencyActionWidget)

        self.__showSecondaryToolBarAction = QWidgetAction(self)
        self.__showSecondaryToolBarChkBox = QCheckBox(LangClass.TRANSLATIONS['Show Secondary Toolbar'])
        self.__showSecondaryToolBarChkBox.setChecked(self.__settingsParamContainer.show_secondary_toolbar)
        self.__showSecondaryToolBarChkBox.toggled.connect(self.__showSecondaryToolBarChkBoxChecked)
        self.__showSecondaryToolBarAction.setDefaultWidget(self.__showSecondaryToolBarChkBox)

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        apiLbl = QLabel(LangClass.TRANSLATIONS['API'])

        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText(LangClass.TRANSLATIONS['Write your API Key...'])
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

        apiWidget = QWidget(self)
        apiWidget.setLayout(lay)

        self.__apiAction = QWidgetAction(self)
        self.__apiAction.setDefaultWidget(apiWidget)

        self.__settingsAction = QAction(LangClass.TRANSLATIONS['Settings'], self)
        self.__settingsAction.setShortcut(DEFAULT_SHORTCUT_SETTING)
        self.__settingsAction.triggered.connect(self.__showSettingsDialog)

    def __fullScreenToggle(self, f):
        if f:
            self.showFullScreen()
        else:
            self.showNormal()

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

        donateMenu = QMenu(LangClass.TRANSLATIONS['Donate'], self)
        donateMenu.addAction(self.__paypalAction)
        donateMenu.addAction(self.__buyMeCoffeeAction)

        menubar.addMenu(donateMenu)

    def __setTrayMenu(self):
        # background app
        menu = QMenu()
        app = QApplication.instance()

        action = QAction("Quit", self)
        action.setIcon(QIcon(ICON_CLOSE))

        action.triggered.connect(app.quit)

        menu.addAction(action)

        tray_icon = QSystemTrayIcon(app)
        tray_icon.setIcon(QIcon(DEFAULT_APP_ICON))
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
        self.__toolbar.addAction(self.__showSecondaryToolBarAction)
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

    def __setApiKeyAndClient(self, api_key):
        # for subprocess (mostly)
        os.environ['OPENAI_API_KEY'] = api_key
        # for showing to the user
        self.__apiLineEdit.setText(api_key)

        OPENAI_STRUCT.api_key = os.environ['OPENAI_API_KEY']

    def __loadApiKeyInIni(self):
        # this api key should be yours
        self.__setApiKeyAndClient(CONFIG_MANAGER.get_general_property('API_KEY'))
        # Set llama index directory if it exists
        init_llama()

    def __setAIEnabled(self, f):
        self.__gptWidget.setAIEnabled(f)
        self.__dallEWidget.setAIEnabled(f)

    def __setApi(self):
        try:
            api_key = self.__apiLineEdit.text()
            response = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {api_key}'})
            f = response.status_code == 200
            self.__setAIEnabled(f)
            if f:
                self.__setApiKeyAndClient(api_key)
                CONFIG_MANAGER.set_general_property('API_KEY', api_key)

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
        aboutDialog = AboutDialog(self)
        aboutDialog.exec()

    def __stackToggle(self, f):
        if f:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def __setTransparency(self, v):
        self.setWindowOpacity(v / 100)

    def __showSecondaryToolBarChkBoxChecked(self, f):
        self.__mainWidget.currentWidget().showSecondaryToolBar(f)
        self.__settingsParamContainer.show_secondary_toolbar = f

    def __executeCustomizeDialog(self):
        dialog = CustomizeDialog(self.__customizeParamsContainer, parent=self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            container = dialog.getParam()
            self.__customizeParamsContainer = container
            self.__refreshContainer(container)
            self.__gptWidget.refreshCustomizedInformation(container)

    def __aiTypeChanged(self, i):
        self.__mainWidget.setCurrentIndex(i)
        widget = self.__mainWidget.currentWidget()
        widget.showSecondaryToolBar(self.__settingsParamContainer.show_secondary_toolbar)

    def __initContainer(self, container):
        """
        Initialize the container with the values in the settings file
        """
        for k, v in container.get_items():
            if not CONFIG_MANAGER.get_general_property(k):
                CONFIG_MANAGER.set_general_property(k, v)
            else:
                setattr(container, k, CONFIG_MANAGER.get_general_property(k))
        if isinstance(container, SettingsParamsContainer):
            self.__lang = LangClass.lang_changed(container.lang)

    def __refreshContainer(self, container):
        if isinstance(container, SettingsParamsContainer):
            prev_db = CONFIG_MANAGER.get_general_property('db')
            prev_show_toolbar = CONFIG_MANAGER.get_general_property('show_toolbar')
            prev_show_secondary_toolbar = CONFIG_MANAGER.get_general_property('show_secondary_toolbar')
            prev_show_as_markdown = CONFIG_MANAGER.get_general_property('show_as_markdown')

            for k, v in container.get_items():
                CONFIG_MANAGER.set_general_property(k, v)

            # If db name is changed
            if container.db != prev_db:
                QMessageBox.information(self, LangClass.TRANSLATIONS['Info'], LangClass.TRANSLATIONS["The name of the reference target database has been changed. The changes will take effect after a restart."])
            # If show_toolbar is changed
            if container.show_toolbar != prev_show_toolbar:
                self.__toolbar.setVisible(container.show_toolbar)
            # If show_secondary_toolbar is changed
            if container.show_secondary_toolbar != prev_show_secondary_toolbar:
                for i in range(self.__mainWidget.count()):
                    currentWidget = self.__mainWidget.widget(i)
                    currentWidget.showSecondaryToolBar(container.show_secondary_toolbar)
            # If properties that require a restart are changed
            if container.lang != self.__lang or container.show_as_markdown != prev_show_as_markdown:
                change_list = []
                if container.lang != self.__lang:
                    change_list.append(LangClass.TRANSLATIONS["Language"])
                if container.show_as_markdown != prev_show_as_markdown:
                    change_list.append(LangClass.TRANSLATIONS["Show as Markdown"])
                result = show_message_box_after_change_to_restart(change_list)
                if result == QMessageBox.StandardButton.Yes:
                    restart_app()

        elif isinstance(container, CustomizeParamsContainer):
            prev_font_family = CONFIG_MANAGER.get_general_property('font_family')
            prev_font_size = CONFIG_MANAGER.get_general_property('font_size')

            for k, v in container.get_items():
                CONFIG_MANAGER.set_general_property(k, v)

            if container.font_family != prev_font_family or container.font_size != prev_font_size:
                change_list = [
                    LangClass.TRANSLATIONS["Font Change"],
                ]
                result = show_message_box_after_change_to_restart(change_list)
                if result == QMessageBox.StandardButton.Yes:
                    restart_app()

    def __refreshColumns(self):
        self.__gptWidget.setColumns(self.__settingsParamContainer.chat_column_to_show)
        image_column_to_show = self.__settingsParamContainer.image_column_to_show
        if image_column_to_show.__contains__('data'):
            image_column_to_show.remove('data')
        self.__dallEWidget.setColumns(self.__settingsParamContainer.image_column_to_show)
        self.__replicateWidget.setColumns(self.__settingsParamContainer.image_column_to_show)

    def __showSettingsDialog(self):
        dialog = SettingsDialog(self.__settingsParamContainer, parent=self)
        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            container = dialog.getParam()
            self.__settingsParamContainer = container
            self.__refreshContainer(container)
            self.__refreshColumns()

    def __doNotAskAgainChanged(self, value):
        self.__settingsParamContainer.do_not_ask_again = value
        self.__refreshContainer(self.__settingsParamContainer)

    def __beforeClose(self):
        if self.__settingsParamContainer.do_not_ask_again:
            app = QApplication.instance()
            app.quit()
        else:
            # Show a message box to confirm the exit or cancel or running in the background
            dialog = DoNotAskAgainDialog(self.__settingsParamContainer.do_not_ask_again, parent=self)
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

    def closeEvent(self, event):
        f = self.__beforeClose()
        if f:
            event.ignore()
        else:
            return super().closeEvent(event)