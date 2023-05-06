import inspect
import json, webbrowser

import openai, requests, os

from chatWidget import Prompt, ChatBrowser

from notifier import NotifierWidget

from qtpy.QtCore import Qt, QCoreApplication, QThread, QSettings, QEvent, Signal
from qtpy.QtGui import QGuiApplication, QFont, QIcon, QColor, QCursor
from qtpy.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QSplitter, QDialog, QSpinBox, \
    QFileDialog, QToolBar, QWidgetAction, QHBoxLayout, QAction, QMenu, \
    QSystemTrayIcon, QMessageBox, QSizePolicy, QLabel, QListWidgetItem, QLineEdit, QPushButton

from pyqt_openai.apiData import getModelEndpoint
from pyqt_openai.clickableTooltip import ClickableTooltip
from pyqt_openai.customizeDialog import CustomizeDialog
from pyqt_openai.leftSideBar import LeftSideBar
from pyqt_openai.apiData import ModelData
from pyqt_openai.prompt.promptGeneratorWidget import PromptGeneratorWidget
from pyqt_openai.right_sidebar.aiPlaygroundWidget import AIPlaygroundWidget
from pyqt_openai.svgButton import SvgButton
from pyqt_openai.sqlite import SqliteDatabase

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support
# qt version should be above 5.14
# todo check the qt version with qtpy
if os.environ['QT_API'] == 'pyqt5' or os.environ['QT_API'] != 'pyside6':
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

QApplication.setFont(QFont('Arial', 12))


class OpenAIThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: user or AI
    Third: streaming a chat completion or not
    Forth: Image generation with DALL-E or not
    """
    replyGenerated = Signal(str, bool, bool, bool)
    streamFinished = Signal()

    def __init__(self, model, openai_arg, is_img, remember_f, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__model = model
        self.__endpoint = getModelEndpoint(model)
        self.__openai_arg = openai_arg
        self.__remember_f = remember_f
        self.__is_img = is_img

    def run(self):
        try:
            if self.__is_img:
                response = openai.Image.create(
                    **self.__openai_arg
                )

                # TODO get a lot of images
                image_url = response['data'][0]['url']

                self.replyGenerated.emit(image_url, False, False, True)
            else:
                if self.__endpoint == '/v1/chat/completions':
                    response = openai.ChatCompletion.create(
                           **self.__openai_arg
                    )
                    # if it is streaming, type will be generator
                    if inspect.isgenerator(response):
                        for chunk in response:
                            delta = chunk['choices'][0]['delta']
                            response_text = delta.get('content', '')
                            if response_text:
                                self.replyGenerated.emit(response_text, False, True, False)
                            else:
                                finish_reason = chunk['choices'][0].get('finish_reason', '')
                                if finish_reason:
                                    self.streamFinished.emit()
                    else:
                        response_text = response['choices'][0]['message']['content']
                        self.replyGenerated.emit(response_text, False, False, False)
                elif self.__endpoint == '/v1/completions':
                    openai_object = openai.Completion.create(
                        **self.__openai_arg
                    )

                    response_text = openai_object['choices'][0]['text'].strip()

                    # this doesn't store any data, so we manually do that every time
                    if self.__remember_f:
                        conv = {
                            'prompt': self.__openai_arg['prompt'],
                            'response': response_text,
                        }

                        with open('conv.json', 'a') as f:
                            f.write(json.dumps(conv) + '\n')

                    self.replyGenerated.emit(response_text, False, False, False)
        except openai.error.InvalidRequestError as e:
            print(e)
            self.replyGenerated.emit('<p style="color:red">Your request was rejected as a result of our safety system.<br/>'
                                     'Your prompt may contain text that is not allowed by our safety system.</p>', False, False, False)
        except openai.error.RateLimitError as e:
            self.replyGenerated.emit(f'<p style="color:red">{e}<br/>Check the usage: https://platform.openai.com/account/usage<br/>Update to paid account: https://platform.openai.com/account/billing/overview', False, False, False)


class OpenAIChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # db
        self.__db = SqliteDatabase()

        # managing with ini file or something else
        self.__ini_etc_dict = {}

        self.__remember_past_conv = False
        self.__finishReason = False
        self.__modelData = ModelData()

        self.__ini_etc_dict['remember_past_conv'] = self.__remember_past_conv
        self.__ini_etc_dict['finishReason'] = self.__finishReason
        self.__ini_etc_dict['modelData'] = self.__modelData

        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        # make it compatible with version which was used json file as a database
        if self.__isConvHistoryJsonExists():
            self.__migrateJsonToSqlite()

        # "remember past conv" feature
        if self.__settings_struct.contains('REMEMBER_PAST_CONVERSATION'):
            self.__remember_past_conv = True if self.__settings_struct.value('REMEMBER_PAST_CONVERSATION') == '1' else False
        else:
            self.__settings_struct.setValue('REMEMBER_PAST_CONVERSATION', '0')

        # don't care about this - just saving past conversation in gpt 3 and below
        if os.path.exists('conv.json'):
            pass
        else:
            with open('conv.json', 'w') as f:
                json.dump({}, f)

    def __isConvHistoryJsonExists(self):
        return os.path.exists('conv_history.json')

    def __migrateJsonToSqlite(self):
        self.__db.convertJsonIntoSql()
        os.remove('conv_history.json')

    def __initUi(self):
        self.setWindowTitle('PyQt OpenAI Chatbot')
        self.setWindowIcon(QIcon('ico/openai.svg'))

        self.__leftSideBarWidget = LeftSideBar()
        self.__browser = ChatBrowser()
        self.__prompt = Prompt()
        self.__lineEdit = self.__prompt.getTextEdit()

        self.__leftSideBarWidget.initHistory(self.__db)
        self.__leftSideBarWidget.added.connect(self.__addConv)
        self.__leftSideBarWidget.changed.connect(self.__changeConv)
        self.__leftSideBarWidget.deleted.connect(self.__deleteConv)
        self.__leftSideBarWidget.convUpdated.connect(self.__updateConv)
        self.__leftSideBarWidget.export.connect(self.__export)

        self.__lineEdit.setPlaceholderText('Write some text...')
        self.__lineEdit.returnPressed.connect(self.__chat)

        self.__browser.convUnitUpdated.connect(self.__updateConvUnit)

        lay = QHBoxLayout()
        lay.addWidget(self.__prompt)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__queryWidget = QWidget()
        self.__queryWidget.setLayout(lay)
        self.__queryWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        lay = QVBoxLayout()
        lay.addWidget(self.__browser)
        lay.addWidget(self.__queryWidget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        chatWidget = QWidget()
        chatWidget.setLayout(lay)

        self.__aiPlaygroundWidget = AIPlaygroundWidget(self.__db, self.__ini_etc_dict, self.__modelData)

        self.__promptGeneratorWidget = PromptGeneratorWidget()

        self.__rightSideBar = QSplitter()
        self.__rightSideBar.setOrientation(Qt.Vertical)
        self.__rightSideBar.addWidget(self.__aiPlaygroundWidget)
        self.__rightSideBar.addWidget(self.__promptGeneratorWidget)
        self.__rightSideBar.setSizes([600, 400])
        self.__rightSideBar.setChildrenCollapsible(False)
        self.__rightSideBar.setHandleWidth(2)
        self.__rightSideBar.setStyleSheet(
        '''
        QSplitter::handle:vertical
        {
            background: #CCC;
            height: 1px;
        }
        ''')

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

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__leftSideBarWidget)
        mainWidget.addWidget(chatWidget)
        mainWidget.addWidget(self.__rightSideBar)
        mainWidget.setSizes([100, 500, 400])
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setHandleWidth(2)
        mainWidget.setStyleSheet(
        '''
        QSplitter::handle:horizontal
        {
            background: #CCC;
            height: 1px;
        }
        ''')

        # set action and toolbar
        self.__setActions()
        self.__setToolBar()

        # load ini file
        self.__loadApiKeyInIni()

        # check if loaded API_KEY from ini file is not empty
        if openai.api_key:
            self.__setApi()
        # if it is empty
        else:
            self.__lineEdit.setEnabled(False)
            self.__apiCheckPreviewLbl.hide()

        self.setCentralWidget(mainWidget)
        self.resize(1024, 768)

        self.__lineEdit.setFocus()

    def __setActions(self):
        self.__stackAction = QWidgetAction(self)
        self.__stackBtn = SvgButton()
        self.__stackBtn.setIcon('ico/stackontop.svg')
        self.__stackBtn.setCheckable(True)
        self.__stackBtn.toggled.connect(self.__stackToggle)
        self.__stackAction.setDefaultWidget(self.__stackBtn)
        self.__stackBtn.setToolTip('Always On Top')

        self.__leftSideBarAction = QWidgetAction(self)
        self.__sideBarBtn = SvgButton()
        self.__sideBarBtn.setIcon('ico/sidebar.svg')
        self.__sideBarBtn.setCheckable(True)
        self.__sideBarBtn.toggled.connect(self.__leftSideBarWidget.setVisible)
        self.__leftSideBarAction.setDefaultWidget(self.__sideBarBtn)
        self.__sideBarBtn.setToolTip('Chat List')
        self.__sideBarBtn.setChecked(True)

        self.__settingAction = QWidgetAction(self)
        self.__settingBtn = SvgButton()
        self.__settingBtn.setIcon('ico/setting.svg')
        self.__settingBtn.toggled.connect(self.__aiPlaygroundWidget.setVisible)
        self.__settingAction.setDefaultWidget(self.__settingBtn)
        self.__settingBtn.setToolTip('Settings')
        self.__settingBtn.setCheckable(True)
        self.__settingBtn.setChecked(True)
        self.__settingBtn.setChecked(False)

        self.__customizeAction = QWidgetAction(self)
        self.__customizeBtn = SvgButton()
        self.__customizeBtn.setIcon('ico/customize.svg')
        self.__customizeBtn.clicked.connect(self.__executeCustomizeDialog)
        self.__customizeAction.setDefaultWidget(self.__customizeBtn)
        self.__customizeBtn.setToolTip('Customize (working)')

        self.__promptAction = QWidgetAction(self)
        self.__promptBtn = SvgButton()
        self.__promptBtn.setIcon('ico/prompt.svg')
        self.__promptAction.setDefaultWidget(self.__promptBtn)
        self.__promptBtn.toggled.connect(self.__promptGeneratorWidget.setVisible)
        self.__promptBtn.setToolTip('Prompt Generator')
        self.__promptBtn.setCheckable(True)
        self.__promptBtn.setChecked(True)
        self.__promptBtn.setChecked(False)

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

        self.__apiCheckPreviewLbl = QLabel('API key is valid')
        self.__apiCheckPreviewLbl.setFont(QFont('Arial', 10))

        self.__apiAction = QWidgetAction(self)
        apiLbl = QLabel('API')

        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText('Write your API Key...')
        self.__apiLineEdit.returnPressed.connect(self.__setApi)
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)

        apiBtn = QPushButton('Use')
        apiBtn.clicked.connect(self.__setApi)

        lay = QHBoxLayout()
        lay.addWidget(apiLbl)
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(apiBtn)
        lay.addWidget(self.__apiCheckPreviewLbl)

        apiWidget = QWidget()
        apiWidget.setLayout(lay)
        self.__apiAction.setDefaultWidget(apiWidget)

    def __activated(self, reason):
        if reason == 3:
            self.show()

    def __setToolBar(self):
        toolbar = QToolBar()
        lay = QHBoxLayout()
        toolbar.addAction(self.__stackAction)
        toolbar.addAction(self.__leftSideBarAction)
        toolbar.addAction(self.__settingAction)
        toolbar.addAction(self.__promptAction)
        toolbar.addAction(self.__customizeAction)
        toolbar.addAction(self.__transparentAction)
        toolbar.addAction(self.__apiAction)
        toolbar.setLayout(lay)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        # QToolbar's layout can't be set spacing with lay.setSpacing so i've just did this instead
        toolbar.setStyleSheet('QToolBar { spacing: 2px; }')

    def eventFilter(self, source, event):
        if event.type() == QEvent.ToolTip and source.toolTip():
            toolTip = ClickableTooltip.showText(
                QCursor.pos(), source.toolTip(), source)
            toolTip.linkActivated.connect(self.toolTipLinkClicked)
            return True
        return super().eventFilter(source, event)

    def toolTipLinkClicked(self, url):
        webbrowser.open(url)

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

    def __setApi(self):
        try:
            api_key = self.__apiLineEdit.text()
            response = requests.get('https://api.openai.com/v1/engines', headers={'Authorization': f'Bearer {api_key}'})
            f = response.status_code == 200
            self.__lineEdit.setEnabled(f)
            if f:
                self.__setApiKey(api_key)
                self.__settings_struct.setValue('API_KEY', api_key)

                self.__aiPlaygroundWidget.setModelInfoByModel(True)

                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(0, 200, 0).name()))
                self.__apiCheckPreviewLbl.setText('API key is valid')
            else:
                raise Exception
        except Exception as e:
            self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(255, 0, 0).name()))
            self.__apiCheckPreviewLbl.setText('API key is invalid')
            self.__lineEdit.setEnabled(False)
            print(e)
        finally:
            self.__apiCheckPreviewLbl.show()

    def __chat(self):
        info_dict = self.__db.selectInfo()
        is_img = info_dict['engine'] in ['DALL-E', 'midjourney', 'stable_diffusion']
        openai_arg = ''
        if is_img:
            openai_arg = {
                "prompt": self.__lineEdit.toPlainText(),
                "n": info_dict['n'],
                "size": f"{info_dict['width']}x{info_dict['height']}"
            }
        else:
            if self.__remember_past_conv:
                convs = []
                with open('conv.json', 'r') as f:
                    for line in f:
                        conv = json.loads(line.strip())
                        convs.append(conv)
            # TODO refactoring
            if info_dict['engine'] in ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'gpt-4']:
                # "assistant" below is for making the AI remember the last question
                openai_arg = {
                    'model': info_dict['engine'],
                    'messages': [
                        {"role": "system", "content": info_dict['system']},
                        {"role": "assistant", "content": self.__browser.getAllText()},
                        {"role": "user", "content": self.__lineEdit.toPlainText()},
                    ],
                    # 'temperature': info_dict['temperature'],

                    # won't use max_tokens, this is set to infinite by default
                    # and i can't find any reason why should i limit the tokens currently
                    # https://platform.openai.com/docs/api-reference/chat/create
                    # 'max_tokens': self.__max_tokens,

                    # 'top_p': info_dict['top_p'],
                    # 'frequency_penalty': info_dict['frequency_penalty'],
                    # 'presence_penalty': info_dict['presence_penalty'],

                    'stream': info_dict['stream'],
                }
            else:
                openai_arg = info_dict
        if self.__leftSideBarWidget.isCurrentConvExists():
            pass
        else:
            self.__addConv()

        self.__lineEdit.setEnabled(False)
        self.__leftSideBarWidget.setEnabled(False)

        self.__browser.showLabel(self.__lineEdit.toPlainText(), True, False, False)

        self.__t = OpenAIThread(info_dict['engine'], openai_arg, is_img, self.__remember_past_conv)
        self.__t.replyGenerated.connect(self.__browser.showLabel)
        self.__t.streamFinished.connect(self.__browser.streamFinished)
        self.__lineEdit.clear()
        self.__t.start()
        self.__t.finished.connect(self.__afterGenerated)

    def __afterGenerated(self):
        self.__lineEdit.setEnabled(True)
        self.__leftSideBarWidget.setEnabled(True)
        self.__lineEdit.setFocus()
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text='Response 👌', detailed_text='Click this!')
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.show)

    def __stackToggle(self, f):
        if f:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def __executeCustomizeDialog(self):
        dialog = CustomizeDialog(self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            pass

    def __setTransparency(self, v):
        self.setWindowOpacity(v / 100)

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

    def __changeConv(self, item: QListWidgetItem):
        # If a 'change' event occurs but there are no items, it should mean that list is empty
        # so reset conv_history.json
        if item:
            id = item.data(Qt.UserRole)
            conv = self.__db.selectConvUnit(id)
            self.__browser.replaceConv(id, conv)
        else:
            self.__browser.resetChatWidget(0)

    def __addConv(self):
        self.__db.insertConv('New Chat')
        cur_id = self.__db.getCursor().lastrowid
        self.__browser.resetChatWidget(cur_id)
        self.__leftSideBarWidget.addToList(cur_id)
        self.__lineEdit.setFocus()

    def __updateConv(self, id, title=None):
        if title:
            self.__db.updateConv(id, title)

    def __deleteConv(self, id_lst):
        for id in id_lst:
            self.__db.deleteConv(id)

    def __export(self, ids):
        filename = QFileDialog.getSaveFileName(self, 'Save', os.path.expanduser('~'), 'SQLite DB file (*.db)')
        if filename[0]:
            filename = filename[0]
            self.__db.export(ids, filename)

    def __updateConvUnit(self, id, user_f, conv_unit=None):
        if conv_unit:
            self.__db.insertConvUnit(id, user_f, conv_unit)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = OpenAIChatBot()
    w.show()
    sys.exit(app.exec())