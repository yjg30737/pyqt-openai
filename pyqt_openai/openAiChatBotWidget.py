import json
import os
import sys
import webbrowser

from qtpy.QtCore import Qt, QSettings
from qtpy.QtWidgets import QHBoxLayout, QWidget, QSizePolicy, QVBoxLayout, QFrame, QSplitter, \
    QFileDialog, QMessageBox, QPushButton

from pyqt_openai.chatNavWidget import ChatNavWidget
from pyqt_openai.chat_widget.chatBrowser import ChatBrowser
from pyqt_openai.chat_widget.chatWidget import ChatWidget
from pyqt_openai.chat_widget.prompt import Prompt
from pyqt_openai.constants import THREAD_TABLE_NAME
from pyqt_openai.models import ChatThreadContainer, ChatMessageContainer
from pyqt_openai.openAiThread import OpenAIThread, LlamaOpenAIThread
from pyqt_openai.prompt_gen_widget.promptGeneratorWidget import PromptGeneratorWidget
from pyqt_openai.pyqt_openai_data import DB, get_argument, LLAMAINDEX_WRAPPER
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.right_sidebar.aiPlaygroundWidget import AIPlaygroundWidget
from pyqt_openai.util.script import open_directory, get_generic_ext_out_of_qt_ext, message_list_to_txt, \
    conv_unit_to_html, \
    add_file_to_zip
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.notifier import NotifierWidget


class OpenAIChatBotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)
        self.__notify_finish = self.__settings_ini.value('notify_finish', type=bool)

        if not self.__settings_ini.contains('show_chat_list'):
            self.__settings_ini.setValue('show_chat_list', True)
        if not self.__settings_ini.contains('show_setting'):
            self.__settings_ini.setValue('show_setting', True)
        if not self.__settings_ini.contains('show_prompt'):
            self.__settings_ini.setValue('show_prompt', True)

        self.__show_chat_list = self.__settings_ini.value('show_chat_list', type=bool)
        self.__show_setting = self.__settings_ini.value('show_setting', type=bool)
        self.__show_prompt = self.__settings_ini.value('show_prompt', type=bool)

        self.__is_showing_favorite = False

    def __initUi(self):
        self.__chatNavWidget = ChatNavWidget(ChatThreadContainer.get_keys(), THREAD_TABLE_NAME)
        self.__chatWidget = ChatWidget()
        self.__browser = self.__chatWidget.getChatBrowser()

        self.__prompt = Prompt()
        self.__prompt.onStoppedClicked.connect(self.__stopResponse)
        self.__prompt.onContinuedClicked.connect(self.__continueResponse)
        self.__prompt.onRegenerateClicked.connect(self.__regenerateResponse)

        self.__lineEdit = self.__prompt.getTextEdit()
        self.__aiPlaygroundWidget = AIPlaygroundWidget()

        try:
            self.__aiPlaygroundWidget.onDirectorySelected.connect(LLAMAINDEX_WRAPPER.set_directory)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        self.__promptGeneratorWidget = PromptGeneratorWidget()

        self.__sideBarBtn = Button()
        self.__sideBarBtn.setStyleAndIcon('ico/sidebar.svg')
        self.__sideBarBtn.setCheckable(True)
        self.__sideBarBtn.setToolTip('Chat List')
        self.__sideBarBtn.setChecked(self.__show_chat_list)
        self.__sideBarBtn.toggled.connect(self.__toggle_sidebar)

        self.__settingBtn = Button()
        self.__settingBtn.setStyleAndIcon('ico/setting.svg')
        self.__settingBtn.setToolTip('Chat Settings')
        self.__settingBtn.setCheckable(True)
        self.__settingBtn.setChecked(self.__show_setting)
        self.__settingBtn.toggled.connect(self.__toggle_setting)

        self.__promptBtn = Button()
        self.__promptBtn.setStyleAndIcon('ico/prompt.svg')
        self.__promptBtn.setToolTip('Prompt Generator')
        self.__promptBtn.setCheckable(True)
        self.__promptBtn.setChecked(self.__show_prompt)
        self.__promptBtn.toggled.connect(self.__toggle_prompt)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        toggleMenuWidgetBtn = QPushButton('Show Menu Widget')
        toggleMenuWidgetBtn.setCheckable(True)
        toggleMenuWidgetBtn.setChecked(True)
        toggleMenuWidgetBtn.toggled.connect(self.__chatWidget.toggleMenuWidget)

        lay = QHBoxLayout()
        lay.addWidget(self.__sideBarBtn)
        lay.addWidget(self.__settingBtn)
        lay.addWidget(self.__promptBtn)
        lay.addWidget(sep)
        lay.addWidget(toggleMenuWidgetBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        self.__chatNavWidget.added.connect(self.__addThread)
        self.__chatNavWidget.clicked.connect(self.__showChat)
        self.__chatNavWidget.cleared.connect(self.__clearChat)
        self.__chatNavWidget.onImport.connect(self.__importChat)
        self.__chatNavWidget.onChatGPTImport.connect(self.__chatGPTImport)
        self.__chatNavWidget.onExport.connect(self.__exportChat)
        self.__chatNavWidget.onFavoriteClicked.connect(self.__showFavorite)

        self.__lineEdit.returnPressed.connect(self.__chat)

        # self.__browser.messageUpdated.connect(self.__updateMessage)

        lay = QHBoxLayout()
        lay.addWidget(self.__prompt)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__queryWidget = QWidget()
        self.__queryWidget.setLayout(lay)
        self.__queryWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        lay = QVBoxLayout()
        lay.addWidget(self.__chatWidget)
        lay.addWidget(self.__queryWidget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        chatWidget = QWidget()
        chatWidget.setLayout(lay)

        self.__rightSideBar = QSplitter()
        self.__rightSideBar.setOrientation(Qt.Orientation.Vertical)
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
        mainWidget.addWidget(self.__chatNavWidget)
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

        # Put this below to prevent the widgets pop up when app is opened
        self.__chatNavWidget.setVisible(self.__show_chat_list)
        self.__aiPlaygroundWidget.setVisible(self.__show_setting)
        self.__promptGeneratorWidget.setVisible(self.__show_prompt)

    def __toggle_sidebar(self, x):
        self.__chatNavWidget.setVisible(x)
        self.__show_chat_list = x
        self.__settings_ini.setValue('show_chat_list', x)

    def __toggle_setting(self, x):
        self.__aiPlaygroundWidget.setVisible(x)
        self.__show_setting = x
        self.__settings_ini.setValue('show_setting', x)

    def __toggle_prompt(self, x):
        self.__promptGeneratorWidget.setVisible(x)
        self.__show_prompt = x
        self.__settings_ini.setValue('show_prompt', x)

    def showThreadToolWidget(self, f):
        self.__chatWidget.toggleMenuWidget(f)

    def showSecondaryToolBar(self, f):
        self.__menuWidget.setVisible(f)

    def toolTipLinkClicked(self, url):
        webbrowser.open(url)

    def setAIEnabled(self, f):
        self.__lineEdit.setEnabled(f)

    def refreshCustomizedInformation(self):
        self.__chatWidget.refreshCustomizedInformation()

    def __chat(self, continue_f=False):
        try:
            # Get necessary parameters
            stream = self.__settings_ini.value('stream', type=bool)
            model = self.__settings_ini.value('model', type=str)
            system = self.__settings_ini.value('system', type=str)
            temperature = self.__settings_ini.value('temperature', type=float)
            max_tokens = self.__settings_ini.value('max_tokens', type=int)
            top_p = self.__settings_ini.value('top_p', type=float)
            frequency_penalty = self.__settings_ini.value('frequency_penalty', type=float)
            presence_penalty = self.__settings_ini.value('presence_penalty', type=float)
            use_llama_index = self.__settings_ini.value('use_llama_index', type=bool)

            # Get image files
            images = self.__prompt.getUploadedImageFiles()

            messages = self.__browser.getMessages()

            cur_text = self.__prompt.getContent()

            # Check llamaindex is available
            is_llama_available = LLAMAINDEX_WRAPPER.get_directory() and use_llama_index
            use_max_tokens = self.__settings_ini.value('use_max_tokens', type=bool)

            openai_param = get_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                                      use_max_tokens, max_tokens,
                                      images,
                                      is_llama_available)

            # If there is no current conversation selected on the list to the left, make a new one.
            if self.__chatWidget.isNew():
                self.__addThread()

            additional_info = {
                'role': 'user',
                'content': cur_text,
                'model_name': openai_param['model'],
                'finish_reason': '',
                'prompt_tokens': '',
                'completion_tokens': '',
                'total_tokens': '',
            }

            container_param = {k: v for k, v in {**openai_param, **additional_info}.items() if k in ChatMessageContainer.get_keys()}
            # Conversation result information after response
            container = ChatMessageContainer(**container_param)

            # For make chatbot continue to respond
            if continue_f:
                query_text = 'Continue to respond.'
            else:
                query_text = self.__prompt.getContent()
            self.__browser.showLabel(query_text, False, container)

            # Run a different thread based on whether the llama-index is enabled or not.
            if is_llama_available:
                self.__t = LlamaOpenAIThread(LLAMAINDEX_WRAPPER, openai_arg=openai_param, query_text=query_text, info=container)
            else:
                self.__t = OpenAIThread(openai_param, info=container)
            self.__t.started.connect(self.__beforeGenerated)
            self.__t.replyGenerated.connect(self.__browser.showLabel)
            self.__t.streamFinished.connect(self.__browser.streamFinished)
            self.__t.start()
            self.__t.finished.connect(self.__afterGenerated)

            # Remove image files widget from the window
            self.__prompt.resetUploadImageFileWidget()
        except Exception as e:
            # get the line of error and filename
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            QMessageBox.critical(self, "Error", f'''
            {str(e)},
            'File: {filename}',
            'Line: {lineno}'
            ''')

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
        self.__lineEdit.setExecuteEnabled(f)
        self.__chatNavWidget.setEnabled(f)
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
            if self.__notify_finish:
                self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = self.__browser.getLastResponse())
                self.__notifierWidget.show()
                self.__notifierWidget.doubleClicked.connect(self.window().show)

    def __showChat(self, id, title):
        self.__showFavorite(False)
        self.__chatNavWidget.activateFavoriteFromParent(False)
        conv_data = DB.selectCertainThreadMessages(id)
        self.__chatWidget.showTitle(title)
        self.__browser.replaceThread(conv_data, id)
        self.__prompt.activateDuringGeneratingWidget(False)
        self.__prompt.activateAfterResponseWidget(False)

    def __clearChat(self):
        self.__chatWidget.showTitle('')
        self.__browser.resetChatWidget(0)
        self.__prompt.activateDuringGeneratingWidget(False)
        self.__prompt.activateAfterResponseWidget(False)

    def __addThread(self):
        title = LangClass.TRANSLATIONS['New Chat']
        cur_id = DB.insertThread(title)
        self.__browser.resetChatWidget(cur_id)
        self.__chatWidget.showTitle(title)
        self.__browser.replaceThread(DB.selectCertainThreadMessages(cur_id), cur_id)
        self.__lineEdit.setFocus()
        self.__chatNavWidget.add(called_from_parent=True)

    def __importChat(self, filename):
        try:
            data = []
            with open(filename, 'r') as f:
                data = json.load(f)

            # Import thread
            for thread in data:
                cur_id = DB.insertThread(thread['name'])
                messages = thread['messages']
                # Import message
                for message in messages:
                    message['thread_id'] = cur_id
                    container = ChatMessageContainer(**message)
                    DB.insertMessage(container)
            self.__chatNavWidget.refreshData()
        except Exception as e:
            QMessageBox.critical(self, "Error", 'Check whether the file is a valid JSON file for importing.')

    def __chatGPTImport(self, data):
        try:
            # Import thread
            for thread in data:
                cur_id = DB.insertThread(thread['name'])
                messages = thread['messages']
                # Import message
                for message in messages:
                    message['thread_id'] = cur_id
                    container = ChatMessageContainer(**message)
                    DB.insertMessage(container)
            self.__chatNavWidget.refreshData()
        except Exception as e:
            QMessageBox.critical(self, "Error", 'Check whether the file is a valid JSON file for importing.')

    def __exportChat(self, ids):
        file_data = QFileDialog.getSaveFileName(self, LangClass.TRANSLATIONS['Save'], os.path.expanduser('~'), 'JSON file (*.json);;txt files Compressed File (*.zip);;html files Compressed File (*.zip)')
        if file_data[0]:
            filename = file_data[0]
            ext = os.path.splitext(filename)[-1] or get_generic_ext_out_of_qt_ext(file_data[1])
            if ext == '.zip':
                compressed_file_type = file_data[1].split(' ')[0].lower()
                ext_dict = {'txt': {'ext':'.txt', 'func':message_list_to_txt}, 'html': {'ext': '.html', 'func':conv_unit_to_html}}
                for id in ids:
                    row_info = DB.selectThread(id)
                    # Limit the title length to file name length
                    title = row_info['name'][:32]
                    txt_filename = f'{title}_{id}{ext_dict[compressed_file_type]["ext"]}'
                    txt_content = ext_dict[compressed_file_type]['func'](DB, id, title)
                    add_file_to_zip(txt_content, txt_filename, os.path.splitext(filename)[0] + '.zip')
            elif ext == '.json':
                DB.export(ids, filename)
            open_directory(os.path.dirname(filename))

    # def __updateMessage(self, arg: ChatMessageContainer):
    #     if arg.content:
    #         DB.insertMessage(arg)

    def setColumns(self, columns):
        self.__chatNavWidget.setColumns(columns)

    def __showFavorite(self, f):
        if f:
            lst = DB.selectFavorite()
            if len(lst) == 0:
                return
            else:
                lst = [ChatMessageContainer(**dict(c)) for c in lst]
                self.__browser.replaceThreadForFavorite(lst)
                # self.__browser.show()
    #             self.__browser.setWindowTitle('Favorite')
    #             self.__browser.setWindowModality(Qt.WindowModality.ApplicationModal)
    #     else:
    #         self.__browser.messageUpdated.connect(self.__updateMessage)
        self.__prompt.setEnabled(not f)
        self.__is_showing_favorite = f
