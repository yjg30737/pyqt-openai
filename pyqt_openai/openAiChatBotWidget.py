import json
import os
import webbrowser

from qtpy.QtCore import Qt, QSettings, QEvent, Signal
from qtpy.QtGui import QCursor
from qtpy.QtWidgets import QHBoxLayout, QWidget, QSizePolicy, QVBoxLayout, QFrame, QSplitter, \
    QListWidgetItem, QFileDialog

from pyqt_openai.apiData import ModelData
from pyqt_openai.chatWidget import Prompt, ChatBrowser
from pyqt_openai.leftSideBar import LeftSideBar
from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.openAiThread import OpenAIThread
from pyqt_openai.prompt.promptGeneratorWidget import PromptGeneratorWidget
from pyqt_openai.right_sidebar.aiPlaygroundWidget import AIPlaygroundWidget
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgButton import SvgButton


class OpenAIChatBotWidget(QWidget):
    notifierWidgetActivated = Signal()

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
            self.__remember_past_conv = True if self.__settings_struct.value(
                'REMEMBER_PAST_CONVERSATION') == '1' else False
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
        self.__leftSideBarWidget = LeftSideBar()
        self.__browser = ChatBrowser()
        self.__prompt = Prompt(self.__db)
        self.__lineEdit = self.__prompt.getTextEdit()
        self.__aiPlaygroundWidget = AIPlaygroundWidget(self.__db, self.__ini_etc_dict, self.__modelData)
        self.__promptGeneratorWidget = PromptGeneratorWidget(self.__db)

        self.__sideBarBtn = SvgButton()
        self.__sideBarBtn.setIcon('ico/sidebar.svg')
        self.__sideBarBtn.setCheckable(True)
        self.__sideBarBtn.setToolTip('Chat List')
        self.__sideBarBtn.setChecked(True)
        self.__sideBarBtn.toggled.connect(self.__leftSideBarWidget.setVisible)

        self.__settingBtn = SvgButton()
        self.__settingBtn.setIcon('ico/setting.svg')
        self.__settingBtn.setToolTip('Settings')
        self.__settingBtn.setCheckable(True)
        self.__settingBtn.setChecked(True)
        self.__settingBtn.setChecked(False)
        self.__settingBtn.toggled.connect(self.__aiPlaygroundWidget.setVisible)

        self.__promptBtn = SvgButton()
        self.__promptBtn.setIcon('ico/prompt.svg')
        self.__promptBtn.setToolTip('Prompt Generator')
        self.__promptBtn.setCheckable(True)
        self.__promptBtn.setChecked(True)
        self.__promptBtn.setChecked(False)
        self.__promptBtn.toggled.connect(self.__promptGeneratorWidget.setVisible)

        lay = QHBoxLayout()
        lay.addWidget(self.__sideBarBtn)
        lay.addWidget(self.__settingBtn)
        lay.addWidget(self.__promptBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__leftSideBarWidget.initHistory(self.__db)
        self.__leftSideBarWidget.added.connect(self.__addConv)
        self.__leftSideBarWidget.changed.connect(self.__changeConv)
        self.__leftSideBarWidget.deleted.connect(self.__deleteConv)
        self.__leftSideBarWidget.convUpdated.connect(self.__updateConv)
        self.__leftSideBarWidget.export.connect(self.__export)

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

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
        lay.addWidget(sep)
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setLayout(lay)

        self.__lineEdit.setFocus()

    def setModelInfoByModel(self, f):
        self.__aiPlaygroundWidget.setModelInfoByModel(f)

    def showAiToolBar(self, f):
        self.__menuWidget.setVisible(f)

    def toolTipLinkClicked(self, url):
        webbrowser.open(url)

    def setAIEnabled(self, f):
        self.__lineEdit.setEnabled(f)

    def __chat(self):
        info_dict = self.__db.selectInfo()
        openai_arg = ''
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
                    {"role": "user", "content": self.__prompt.getContent()},
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

        self.__browser.showLabel(self.__prompt.getContent(), True, False)

        self.__t = OpenAIThread(info_dict['engine'], openai_arg, self.__remember_past_conv)
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
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)

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