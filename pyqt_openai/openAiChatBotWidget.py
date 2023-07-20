import json
import os
import webbrowser

from qtpy.QtCore import Qt, QSettings, Signal
from qtpy.QtWidgets import QHBoxLayout, QWidget, QSizePolicy, QVBoxLayout, QFrame, QSplitter, \
    QListWidgetItem, QFileDialog, QMessageBox

from pyqt_openai.apiData import ModelData, getChatModel
from pyqt_openai.chat_widget.chatBrowser import ChatBrowser
from pyqt_openai.chat_widget.prompt import Prompt
from pyqt_openai.leftSideBar import LeftSideBar
from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.openAiThread import OpenAIThread, LlamaOpenAIThread
from pyqt_openai.prompt_gen_widget.promptGeneratorWidget import PromptGeneratorWidget
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.right_sidebar.aiPlaygroundWidget import AIPlaygroundWidget
from pyqt_openai.util.llamapage_script import GPTLLamaIndexClass
from pyqt_openai.util.script import open_directory, get_generic_ext_out_of_qt_ext, conv_unit_to_txt, conv_unit_to_html, \
    add_file_to_zip
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

        # ini
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        if not self.__settings_ini.contains('finish_reason'):
            self.__settings_ini.setValue('finish_reason', False)
        self.__finish_reason = self.__settings_ini.value('finish_reason', type=bool)

        # llamaindex
        self.__llama_class = GPTLLamaIndexClass()

    def __initUi(self):
        self.__leftSideBarWidget = LeftSideBar()
        self.__browser = ChatBrowser(self.__finish_reason)

        self.__prompt = Prompt(self.__db)
        self.__prompt.onStoppedClicked.connect(self.__stopResponse)
        self.__prompt.onContinuedClicked.connect(self.__continueResponse)
        self.__prompt.onRegenerateClicked.connect(self.__regenerateResponse)

        self.__lineEdit = self.__prompt.getTextEdit()
        self.__aiPlaygroundWidget = AIPlaygroundWidget()
        self.__aiPlaygroundWidget.onDirectorySelected.connect(self.__llama_class.set_directory)
        self.__aiPlaygroundWidget.onFinishReasonToggled.connect(self.__onFinishReasonToggled)
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
        self.__settingBtn.toggled.connect(self.__aiPlaygroundWidget.setVisible)

        self.__promptBtn = SvgButton()
        self.__promptBtn.setIcon('ico/prompt.svg')
        self.__promptBtn.setToolTip('Prompt Generator')
        self.__promptBtn.setCheckable(True)
        self.__promptBtn.setChecked(True)
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

    def showAiToolBar(self, f):
        self.__menuWidget.setVisible(f)

    def toolTipLinkClicked(self, url):
        webbrowser.open(url)

    def setAIEnabled(self, f):
        self.__lineEdit.setEnabled(f)

    def __chat(self, continue_f=False):
        try:
            stream = self.__settings_ini.value('stream', type=bool)
            model = self.__settings_ini.value('model', type=str)
            system = self.__settings_ini.value('system', type=str)
            temperature = self.__settings_ini.value('temperature', type=float)
            max_tokens = self.__settings_ini.value('max_tokens', type=int)
            top_p = self.__settings_ini.value('top_p', type=float)
            frequency_penalty = self.__settings_ini.value('frequency_penalty', type=float)
            presence_penalty = self.__settings_ini.value('presence_penalty', type=float)
            use_llama_index = self.__settings_ini.value('use_llama_index', type=bool)

            openai_arg = {
                'model': model,
                'messages': [
                    {"role": "system", "content": system},
                    {"role": "assistant", "content": self.__browser.getAllText()},
                    {"role": "user", "content": self.__prompt.getContent()},
                ],
                'temperature': temperature,
                'top_p': top_p,
                'frequency_penalty': frequency_penalty,
                'presence_penalty': presence_penalty,
                'stream': stream,
            }

            is_llama_available = self.__llama_class.get_directory() and use_llama_index
            # check llamaindex is available
            if is_llama_available:
                del openai_arg['messages']
            use_max_tokens = self.__settings_ini.value('use_max_tokens', type=bool)
            if use_max_tokens:
                openai_arg['max_tokens'] = max_tokens

            if self.__leftSideBarWidget.isCurrentConvExists():
                pass
            else:
                self.__addConv()

            """
            for make GPT continue to respond
            """
            if continue_f:
                query_text = 'Continue to respond.'
            else:
                query_text = self.__prompt.getContent()
            self.__browser.showLabel(query_text, True, False)

            if is_llama_available:
                self.__t = LlamaOpenAIThread(self.__llama_class, openai_arg=openai_arg, query_text=query_text)
            else:
                self.__t = OpenAIThread(model, openai_arg)
            self.__t.started.connect(self.__beforeGenerated)
            self.__t.replyGenerated.connect(self.__browser.showLabel)
            self.__t.streamFinished.connect(self.__browser.streamFinished)
            self.__t.start()
            self.__t.finished.connect(self.__afterGenerated)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def __stopResponse(self):
        self.__t.stop_streaming()

    def __continueResponse(self):
        self.__chat(True)

    def __regenerateResponse(self):
        # TODO
        """
        get last question and make it another response based on it
        """
        pass

    def __toggleWidgetWhileChatting(self, f, continue_f=False):
        self.__lineEdit.setEnabled(f)
        self.__leftSideBarWidget.setEnabled(f)
        self.__prompt.activateDuringGeneratingWidget(not f)
        # TODO
        # self.__prompt.activateAfterResponseWidget(f, continue_f)

    def __beforeGenerated(self):
        self.__toggleWidgetWhileChatting(False)
        self.__lineEdit.clear()

    def __afterGenerated(self):
        continue_f = self.__browser.getLastFinishReason() == 'Finish Reason: length'
        self.__toggleWidgetWhileChatting(True, continue_f)
        self.__lineEdit.setFocus()
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = self.__browser.getLastResponse())
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)

    def __changeConv(self, item: QListWidgetItem):
        if item:
            id = item.data(Qt.UserRole)
            conv_data = self.__db.selectCertainConvHistory(id)
            self.__browser.replaceConv(id, conv_data)
        else:
            self.__browser.resetChatWidget(0)
        self.__prompt.activateDuringGeneratingWidget(False)
        self.__prompt.activateAfterResponseWidget(False)

    def __addConv(self):
        cur_id = self.__db.insertConv(LangClass.TRANSLATIONS['New Chat'])
        self.__browser.resetChatWidget(cur_id)
        self.__leftSideBarWidget.addToList(cur_id)
        self.__lineEdit.setFocus()

    def __updateConv(self, id, title=None):
        if title:
            self.__db.updateConv(id, title)

    def __deleteConv(self, id_lst):
        for id in id_lst:
            self.__db.deleteConv(id)

    def __onFinishReasonToggled(self, f):
        self.__browser.toggle_show_finished_reason_f(f)

    def __export(self, ids):
        file_data = QFileDialog.getSaveFileName(self, LangClass.TRANSLATIONS['Save'], os.path.expanduser('~'), 'SQLite DB file (*.db);;txt files Compressed File (*.zip);;html files Compressed File (*.zip)')
        if file_data[0]:
            filename = file_data[0]
            ext = os.path.splitext(filename)[-1] or get_generic_ext_out_of_qt_ext(file_data[1])
            if ext == '.zip':
                compressed_file_type = file_data[1].split(' ')[0].lower()
                ext_dict = {'txt': {'ext':'.txt', 'func':conv_unit_to_txt}, 'html': {'ext':'.html', 'func':conv_unit_to_html}}
                for id in ids:
                    title = self.__db.selectConv(id)[1]
                    txt_filename = f'{title}{ext_dict[compressed_file_type]["ext"]}'
                    txt_content = ext_dict[compressed_file_type]['func'](self.__db, id, title)
                    add_file_to_zip(txt_content, txt_filename, os.path.splitext(filename)[0] + '.zip')
            elif ext == '.db':
                self.__db.export(ids, filename)
            open_directory(os.path.dirname(filename))

    def __updateConvUnit(self, id, user_f, conv_unit=None, finish_reason=''):
        if conv_unit:
            self.__db.insertConvUnit(id, user_f, conv_unit, finish_reason=finish_reason)