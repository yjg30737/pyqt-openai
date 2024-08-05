import os

import requests
from qtpy.QtCore import Qt, QSettings
from qtpy.QtGui import QFont, QIcon, QColor
from qtpy.QtWidgets import QToolBar, QHBoxLayout, QDialog, QLineEdit, QPushButton, QWidgetAction, QSpinBox, \
    QLabel, QWidget, QApplication, \
    QComboBox, QSizePolicy, QStackedWidget, QMenu, QSystemTrayIcon, \
    QMessageBox, QCheckBox, QAction

from pyqt_openai import INI_FILE_NAME, DEFAULT_SHORTCUT_FULL_SCREEN, \
    APP_INITIAL_WINDOW_SIZE, APP_NAME, APP_ICON, ICON_STACKONTOP, ICON_CUSTOMIZE, ICON_FULLSCREEN, ICON_CLOSE, \
    DEFAULT_SHORTCUT_SETTING, TRANSPARENT_RANGE, TRANSPARENT_INIT_VAL
from pyqt_openai.aboutDialog import AboutDialog
from pyqt_openai.customizeDialog import CustomizeDialog
from pyqt_openai.dalle_widget.dalleMainWidget import DallEMainWidget
from pyqt_openai.doNotAskAgainDialog import DoNotAskAgainDialog
from pyqt_openai.gpt_widget.gptMainWidget import GPTMainWidget
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import SettingsParamsContainer, CustomizeParamsContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT, LLAMAINDEX_WRAPPER
from pyqt_openai.replicate_widget.replicateMainWidget import ReplicateMainWidget
from pyqt_openai.settingsDialog import SettingsDialog
from pyqt_openai.util.script import restart_app, show_message_box_after_change_to_restart, goPayPal, goBuyMeCoffee
from pyqt_openai.widgets.button import Button


class AIWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_struct = QSettings(INI_FILE_NAME, QSettings.Format.IniFormat)
        self.__settingsParamContainer = SettingsParamsContainer()
        self.__customizeParamsContainer = CustomizeParamsContainer()

        self.__initContainer(self.__settingsParamContainer)
        self.__initContainer(self.__customizeParamsContainer)

    def __initUi(self):
        self.setWindowTitle(APP_NAME)

        self.__gptWidget = GPTMainWidget(self)
        self.__dallEWidget = DallEMainWidget(self)
        self.__replicateWidget = ReplicateMainWidget(self)

        self.addWidget(self.__gptWidget)
        self.addWidget(self.__dallEWidget)
        self.addWidget(self.__replicateWidget)

        # load ini file
        self.__loadApiKeyInIni()

        # check if loaded API_KEY from ini file is not empty
        if os.environ['OPENAI_API_KEY']:
            self.__setApi()
        # if it is empty
        else:
            self.__setAIEnabled(False)
            self.__apiCheckPreviewLbl.hide()

        self.resize(*APP_INITIAL_WINDOW_SIZE)

        self.__refreshColumns()
        self.__gptWidget.refreshCustomizedInformation(self.__customizeParamsContainer)

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
        if self.__settings_struct.contains('llama_index_directory') and self.__settings_struct.value('use_llama_index', False, type=bool):
            LLAMAINDEX_WRAPPER.set_directory(self.__settings_struct.value('llama_index_directory'))

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

    def __showAiToolBarChkBoxChecked(self, f):
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
        self.setCurrentIndex(i)
        widget = self.currentWidget()
        widget.showSecondaryToolBar(self.__settingsParamContainer.show_secondary_toolbar)

    def __initContainer(self, container):
        """
        Initialize the container with the values in the settings file
        """
        for k, v in container.get_items():
            if not self.__settings_struct.contains(k):
                self.__settings_struct.setValue(k, v)
            else:
                setattr(container, k, self.__settings_struct.value(k, type=type(v)))
        if isinstance(container, SettingsParamsContainer):
            self.__lang = LangClass.lang_changed(container.lang)

    def __refreshContainer(self, container):
        if isinstance(container, SettingsParamsContainer):
            prev_db = self.__settings_struct.value('db')
            prev_show_toolbar = self.__settings_struct.value('show_toolbar', type=bool)
            prev_show_secondary_toolbar = self.__settings_struct.value('show_secondary_toolbar', type=bool)
            prev_thread_tool_widget = self.__settings_struct.value('thread_tool_widget', type=bool)
            prev_show_as_markdown = self.__settings_struct.value('show_as_markdown', type=bool)

            for k, v in container.get_items():
                self.__settings_struct.setValue(k, v)

            # If db name is changed
            if container.db != prev_db:
                QMessageBox.information(self, LangClass.TRANSLATIONS['Info'], LangClass.TRANSLATIONS["The name of the reference target database has been changed. The changes will take effect after a restart."])
            # If show_toolbar is changed
            if container.show_toolbar != prev_show_toolbar:
                self.__toolbar.setVisible(container.show_toolbar)
            # If show_secondary_toolbar is changed
            if container.show_secondary_toolbar != prev_show_secondary_toolbar:
                for i in range(self.count()):
                    currentWidget = self.widget(i)
                    currentWidget.showSecondaryToolBar(container.show_secondary_toolbar)
            # If thread_tool_widget is changed
            if container.thread_tool_widget != prev_thread_tool_widget:
                if isinstance(self.currentWidget(), GPTMainWidget):
                    self.currentWidget().showThreadToolWidget(container.thread_tool_widget)
            # If properties that require a restart are changed
            if container.lang != self.__lang or container.show_as_markdown != prev_show_as_markdown:
                change_list = []
                if container.lang != self.__lang:
                    change_list.append(LangClass.TRANSLATIONS["Language"])
                if container.show_as_markdown != prev_show_as_markdown:
                    change_list.append(LangClass.TRANSLATIONS["Show as Markdown"])
                result = show_message_box_after_change_to_restart(change_list)
                if result == QMessageBox.StandardButton.Yes:
                    restart_app(settings=self.__settings_struct)

        elif isinstance(container, CustomizeParamsContainer):
            prev_font_family = self.__settings_struct.value('font_family')
            prev_font_size = self.__settings_struct.value('font_size', type=int)

            for k, v in container.get_items():
                self.__settings_struct.setValue(k, v)

            if container.font_family != prev_font_family or container.font_size != prev_font_size:
                change_list = [
                    LangClass.TRANSLATIONS["Font Change"],
                ]
                result = show_message_box_after_change_to_restart(change_list)
                if result == QMessageBox.StandardButton.Yes:
                    restart_app(settings=self.__settings_struct)

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