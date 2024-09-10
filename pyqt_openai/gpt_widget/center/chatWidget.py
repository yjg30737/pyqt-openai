import json
import sys

from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.gpt_widget.center.chatBrowser import ChatBrowser
from pyqt_openai.gpt_widget.center.gptHome import GPTHome
from pyqt_openai.gpt_widget.center.menuWidget import MenuWidget
from pyqt_openai.gpt_widget.center.prompt import Prompt
from pyqt_openai.gpt_widget.gptThread import LlamaOpenAIThread, GPTThread
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.pyqt_openai_data import LLAMAINDEX_WRAPPER, get_argument, DB
from pyqt_openai.widgets.notifier import NotifierWidget
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout, QMessageBox


class ChatWidget(QWidget):
    addThread = Signal()
    onMenuCloseClicked = Signal()

    def __init__(self, parent=None):
        super(ChatWidget, self).__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__cur_id = 0
        self.__notify_finish = CONFIG_MANAGER.get_general_property('notify_finish')
        self.__maximum_messages_in_parameter = CONFIG_MANAGER.get_general_property('maximum_messages_in_parameter')

    def __initUi(self):
        # Main widget
        # This contains home page (at the beginning of the stack) and
        # widget for main view
        self.__mainWidget = QStackedWidget()

        self.__homePage = GPTHome()
        self.__browser = ChatBrowser()
        self.__browser.onReplacedCurrentPage.connect(self.__mainWidget.setCurrentIndex)

        self.__menuWidget = MenuWidget(self.__browser)
        self.__menuWidget.onMenuCloseClicked.connect(self.__onMenuCloseClicked)
        self.__menuWidget.setVisible(False)

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
        lay.addWidget(self.__browser)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        chatWidget = QWidget()
        chatWidget.setLayout(lay)

        self.__mainWidget.addWidget(self.__homePage)
        self.__mainWidget.addWidget(chatWidget)

        self.__prompt = Prompt(self)
        self.__prompt.onStoppedClicked.connect(self.__stopResponse)
        self.__mainPrompt = self.__prompt.getMainPromptInput()

        lay = QHBoxLayout()
        lay.addWidget(self.__prompt)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__queryWidget = QWidget()
        self.__queryWidget.setLayout(lay)
        self.__queryWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        lay = QVBoxLayout()
        lay.addWidget(self.__mainWidget)
        lay.addWidget(self.__queryWidget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__mainPrompt.setFocus()

        self.setLayout(lay)

        self.__mainPrompt.returnPressed.connect(self.__chat)

    def showTitle(self, title):
        self.__menuWidget.setTitle(title)

    def getChatBrowser(self):
        return self.__browser

    def toggleMenuWidget(self, f):
        self.__menuWidget.setVisible(f)
        self.__menuWidget.getFindTextWidget().clearFormatting()

    def __onMenuCloseClicked(self):
        self.__mainPrompt.setFocus()
        self.onMenuCloseClicked.emit()

    def setAIEnabled(self, f):
        self.__prompt.setEnabled(f)

    def refreshCustomizedInformation(self, background_image=None, user_image=None, ai_image=None):
        self.__homePage.setPixmap(background_image)
        self.__browser.setUserImage(user_image)
        self.__browser.setAIImage(ai_image)

    def setCurId(self, id):
        self.__cur_id = id
        self.__browser.setCurId(id)

    def getCurId(self):
        return self.__cur_id

    def __chat(self):
        try:
            # Get necessary parameters
            stream = CONFIG_MANAGER.get_general_property('stream')
            model = CONFIG_MANAGER.get_general_property('model')
            system = CONFIG_MANAGER.get_general_property('system')
            temperature = CONFIG_MANAGER.get_general_property('temperature')
            max_tokens = CONFIG_MANAGER.get_general_property('max_tokens')
            top_p = CONFIG_MANAGER.get_general_property('top_p')
            is_json_response_available = 1 if CONFIG_MANAGER.get_general_property('json_object') else 0
            frequency_penalty = CONFIG_MANAGER.get_general_property('frequency_penalty')
            presence_penalty = CONFIG_MANAGER.get_general_property('presence_penalty')
            use_llama_index = CONFIG_MANAGER.get_general_property('use_llama_index')
            use_max_tokens = CONFIG_MANAGER.get_general_property('use_max_tokens')

            # Get image files
            images = self.__prompt.getImageBuffers()

            messages = self.__browser.getMessages(self.__maximum_messages_in_parameter)

            cur_text = self.__prompt.getContent()

            json_content = self.__prompt.getJSONContent()

            is_llama_available = False
            if use_llama_index:
                # Check llamaindex is available
                is_llama_available = LLAMAINDEX_WRAPPER.get_directory() != ''
                if is_llama_available:
                    if LLAMAINDEX_WRAPPER.is_query_engine_set():
                        pass
                    else:
                        LLAMAINDEX_WRAPPER.set_query_engine(streaming=stream, similarity_top_k=3)
                else:
                    QMessageBox.warning(self, LangClass.TRANSLATIONS["Warning"], LangClass.TRANSLATIONS['LLAMA index is not available. Please check the directory path or disable the llama index.'])
                    return

            # Check JSON response is valid
            if is_json_response_available:
                if not json_content:
                    QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], LangClass.TRANSLATIONS['JSON content is empty. Please fill in the JSON content field.'])
                    return
                try:
                    json.loads(json_content)
                except Exception as e:
                    QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], f'{LangClass.TRANSLATIONS["JSON content is not valid. Please check the JSON content field."]}\n\n{e}')
                    return

            # Get parameters for OpenAI
            openai_param = get_argument(model, system, messages, cur_text, temperature, top_p, frequency_penalty, presence_penalty, stream,
                                      use_max_tokens, max_tokens,
                                      images,
                                      is_llama_available, is_json_response_available, json_content)

            # If there is no current conversation selected on the list to the left, make a new one.
            if self.__mainWidget.currentIndex() == 0:
                self.addThread.emit()

            # Additional information of user's input
            additional_info = {
                'role': 'user',
                'content': cur_text,
                'model_name': openai_param['model'],
                'finish_reason': '',
                'prompt_tokens': '',
                'completion_tokens': '',
                'total_tokens': '',

                'is_json_response_available': is_json_response_available,
            }

            container_param = {k: v for k, v in {**openai_param, **additional_info}.items() if k in ChatMessageContainer.get_keys()}

            # Create a container for the user's input and output from the chatbot
            container = ChatMessageContainer(**container_param)

            query_text = self.__prompt.getContent()
            self.__browser.showLabel(query_text, False, container)

            # Run a different thread based on whether the llama-index is enabled or not.
            if is_llama_available:
                self.__t = LlamaOpenAIThread(openai_param, container, LLAMAINDEX_WRAPPER, query_text)
            else:
                self.__t = GPTThread(openai_param, info=container)
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
            QMessageBox.critical(self, LangClass.TRANSLATIONS["Error"], f'''
                {str(e)},
                'File: {filename}',
                'Line: {lineno}'
            ''')

    def __stopResponse(self):
        self.__t.stop_streaming()

    def __toggleWidgetWhileChatting(self, f):
        self.__mainPrompt.setExecuteEnabled(f)
        self.__prompt.showWidgetInPromptDuringResponse(not f)
        self.__prompt.sendEnabled(f)

    def __beforeGenerated(self):
        self.__toggleWidgetWhileChatting(False)
        self.__mainPrompt.clear()

    def __afterGenerated(self):
        self.__toggleWidgetWhileChatting(True)
        self.__mainPrompt.setFocus()
        if not self.isVisible() or not self.window().isActiveWindow():
            if self.__notify_finish:
                self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = self.__browser.getLastResponse())
                self.__notifierWidget.show()
                self.__notifierWidget.doubleClicked.connect(self.__bringWindowToFront)

    def __bringWindowToFront(self):
        window = self.window()
        window.showNormal()
        window.raise_()
        window.activateWindow()

    def toggleJSON(self, f):
        self.__prompt.toggleJSON(f)

    def showMessages(self, cur_id):
        self.__browser.resetChatWidget(cur_id)
        self.__browser.replaceThread(DB.selectCertainThreadMessages(cur_id), cur_id)
        self.__mainPrompt.setFocus()
        # Reset menu widget
        self.__menuWidget.getFindTextWidget().clearFormatting()

    def clearMessages(self):
        self.__browser.resetChatWidget(0)