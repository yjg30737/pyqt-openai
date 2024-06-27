import os, sys
import webbrowser

from qtpy.QtCore import Qt, QSettings
from qtpy.QtWidgets import QHBoxLayout, QWidget, QSizePolicy, QVBoxLayout, QFrame, QSplitter, \
    QListWidgetItem, QFileDialog, QMessageBox, QPushButton

from pyqt_openai.chat_widget.chatWidget import ChatWidget
from pyqt_openai.chat_widget.prompt import Prompt
from pyqt_openai.leftSideBar import LeftSideBar
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.openAiThread import OpenAIThread, LlamaOpenAIThread
from pyqt_openai.prompt_gen_widget.promptGeneratorWidget import PromptGeneratorWidget
from pyqt_openai.pyqt_openai_data import DB, get_argument, LLAMAINDEX_WRAPPER
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.right_sidebar.aiPlaygroundWidget import AIPlaygroundWidget
from pyqt_openai.widgets.svgButton import SvgButton
from pyqt_openai.util.script import open_directory, get_generic_ext_out_of_qt_ext, conv_unit_to_txt, conv_unit_to_html, \
    add_file_to_zip


class OpenAIChatBotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # ini
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)

    def __initUi(self):
        self.__leftSideBarWidget = LeftSideBar()
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

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)

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
        lay.setAlignment(Qt.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__leftSideBarWidget.initHistory()
        self.__leftSideBarWidget.added.connect(self.__addConv)
        self.__leftSideBarWidget.changed.connect(self.__changeConv)
        self.__leftSideBarWidget.deleted.connect(self.__deleteConv)
        self.__leftSideBarWidget.convUpdated.connect(self.__updateConv)
        self.__leftSideBarWidget.onImport.connect(self.__importConv)
        self.__leftSideBarWidget.onExport.connect(self.__exportConv)

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
        lay.addWidget(self.__chatWidget)
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

            openai_arg = get_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                                      use_max_tokens, max_tokens,
                                      images,
                                      is_llama_available)

            # If there is no current conversation selected on the list to the left, make a new one.
            if self.__leftSideBarWidget.isCurrentConvExists():
                pass
            else:
                self.__addConv()

            # Conversation result information after response
            info = {
                'model_name': openai_arg['model'],
                'finish_reason': '',
                'prompt_tokens': '',
                'completion_tokens': '',
                'total_tokens': '',
            }

            """
            for make GPT continue to respond
            """
            if continue_f:
                query_text = 'Continue to respond.'
            else:
                query_text = self.__prompt.getContent()
            self.__browser.showLabel(query_text, True, False, info)

            # Run a different thread based on whether the llama-index is enabled or not.
            if is_llama_available:
                self.__t = LlamaOpenAIThread(LLAMAINDEX_WRAPPER, openai_arg=openai_arg, query_text=query_text, info=info)
            else:
                self.__t = OpenAIThread(model, openai_arg, info=info)
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
            self.__notifierWidget.doubleClicked.connect(self.window().show)

    def __changeConv(self, item: QListWidgetItem):
        if item:
            id = item.data(Qt.UserRole)
            conv_data = DB.selectCertainConv(id)
            self.__browser.replaceConv(id, conv_data)
        else:
            self.__browser.resetChatWidget(0)
        self.__prompt.activateDuringGeneratingWidget(False)
        self.__prompt.activateAfterResponseWidget(False)

    def __addConv(self):
        cur_id = DB.insertConv(LangClass.TRANSLATIONS['New Chat'])
        self.__browser.resetChatWidget(cur_id)
        self.__leftSideBarWidget.addToList(cur_id)
        self.__lineEdit.setFocus()

    def __updateConv(self, id, title=None):
        if title:
            DB.updateConv(id, title)

    def __deleteConv(self, id_lst):
        for id in id_lst:
            DB.deleteConv(id)

    def __importConv(self, filename):
        old_conv = DB.selectAllConv()
        if old_conv and len(old_conv) > 0:
            message = '''
            There are already conversations. Would you export them before importing? 
            Warning: If you do not export, you will lose the current conversations.
            '''
            messageBox = QMessageBox(self)
            messageBox.setWindowTitle('Information')
            messageBox.setText(message)
            messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            reply = messageBox.exec()
            if reply == QMessageBox.Yes:
                # Export previous conversation
                self.__exportConv([_['id'] for _ in old_conv])
            else:
                pass
        else:
            print(f'Import {filename}')

    def __exportConv(self, ids):
        file_data = QFileDialog.getSaveFileName(self, LangClass.TRANSLATIONS['Save'], os.path.expanduser('~'), 'SQLite DB file (*.db);;txt files Compressed File (*.zip);;html files Compressed File (*.zip)')
        if file_data[0]:
            filename = file_data[0]
            ext = os.path.splitext(filename)[-1] or get_generic_ext_out_of_qt_ext(file_data[1])
            if ext == '.zip':
                compressed_file_type = file_data[1].split(' ')[0].lower()
                ext_dict = {'txt': {'ext':'.txt', 'func':conv_unit_to_txt}, 'html': {'ext':'.html', 'func':conv_unit_to_html}}
                for id in ids:
                    title = DB.selectConv(id)[1]
                    txt_filename = f'{title}{ext_dict[compressed_file_type]["ext"]}'
                    txt_content = ext_dict[compressed_file_type]['func'](DB, id, title)
                    add_file_to_zip(txt_content, txt_filename, os.path.splitext(filename)[0] + '.zip')
            elif ext == '.db':
                DB.export(ids, filename)
            open_directory(os.path.dirname(filename))

    def __updateConvUnit(self, id, user_f, conv_unit=None, info=None):
        if conv_unit:
            DB.insertConvUnit(id, user_f, conv_unit, info=info)