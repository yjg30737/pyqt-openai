from PySide6.QtGui import QPalette

from pyqt_openai import ICON_FAVORITE_NO, ICON_INFO, ICON_FAVORITE_YES, ICON_SPEAKER, WHISPER_TTS_MODEL
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.gpt_widget.center.chatUnit import ChatUnit
from pyqt_openai.gpt_widget.center.responseInfoDialog import ResponseInfoDialog
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.globals import DB, stream_to_speakers
from pyqt_openai.widgets.button import Button


class AIChatUnit(ChatUnit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initAIChatUi()

    def __initVal(self):
        self.__result_info = ''
        self.__show_as_markdown = CONFIG_MANAGER.get_general_property('show_as_markdown')

    def __initAIChatUi(self):
        self.__favoriteBtn = Button()
        self.__favoriteBtn.setStyleAndIcon(ICON_FAVORITE_NO)
        self.__favoriteBtn.setCheckable(True)
        self.__favoriteBtn.toggled.connect(self.__favorite)

        self.__infoBtn = Button()
        self.__infoBtn.setStyleAndIcon(ICON_INFO)
        self.__infoBtn.clicked.connect(self.__showResponseInfoDialog)

        self.__speakerBtn = Button()
        self.__speakerBtn.setStyleAndIcon(ICON_SPEAKER)
        self.__speakerBtn.setCheckable(True)
        self.__speakerBtn.toggled.connect(self.__speak)
        self.thread = None

        self.getMenuWidget().layout().insertWidget(2, self.__favoriteBtn)
        self.getMenuWidget().layout().insertWidget(3, self.__infoBtn)
        self.getMenuWidget().layout().insertWidget(4, self.__speakerBtn)

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase)
        self.setAutoFillBackground(True)

    def __favorite(self, f, insert_f=True):
        favorite = 1 if f else 0
        if favorite:
            self.__favoriteBtn.setStyleAndIcon(ICON_FAVORITE_YES)
        else:
            self.__favoriteBtn.setStyleAndIcon(ICON_FAVORITE_NO)
        if insert_f and self.__result_info:
            current_date = DB.updateMessage(self.__result_info.id, favorite)
            self.__result_info.favorite = favorite
            self.__result_info.favorite_set_date = current_date

    def __showResponseInfoDialog(self):
        if self.__result_info:
            dialog = ResponseInfoDialog(self.__result_info, parent=self)
            dialog.exec()

    def afterResponse(self, arg):
        self.toggleGUI(True)
        self.__result_info = arg
        self.__favorite(True if arg.favorite else False, insert_f=False)

        if arg.is_json_response_available:
            self.getLbl().setJson(arg.content)
        else:
            self.getLbl().setMarkdown(arg.content)
        self.getLbl().adjustBrowserHeight()

    def toggleGUI(self, f: bool):
        self.__favoriteBtn.setEnabled(f)
        self._copyBtn.setEnabled(f)
        self.__infoBtn.setEnabled(f)
        self.__speakerBtn.setEnabled(f)

    def __setResponseInfo(self, arg: ChatMessageContainer):
        self.__result_info = arg
        self.__favorite(True if arg.favorite else False, insert_f=False)

    def getResponseInfo(self):
        """
        Get the response information
        :return: ChatMessageContainer

        Note: This function is used to get the response information after the response is generated.
        """
        try:
            if self.__result_info and isinstance(self.__result_info, ChatMessageContainer):
                return self.__result_info
            else:
                raise AttributeError('Response information is not available')
        except AttributeError as e:
            raise e

    def __speak(self, f):
        if f:
            text = self._lbl.toPlainText()
            if text:
                # Stop the previous thread if it is running
                if self.thread:
                    self.thread.stop()
                    self.thread.join()
                    self.thread = None

                args = {
                    'model': WHISPER_TTS_MODEL,
                    'voice': CONFIG_MANAGER.get_general_property('voice'),
                    'input': text,
                    'speed': CONFIG_MANAGER.get_general_property('voice_speed'),
                }
                self.thread = stream_to_speakers(args, self.__on_thread_complete)
                if not self.thread:
                    self.__speakerBtn.setStyleAndIcon(ICON_SPEAKER)
                    self.__speakerBtn.setChecked(False)
        else:
            if self.thread:
                self.thread.stop()
                self.thread = None
            self.__speakerBtn.setStyleAndIcon(ICON_SPEAKER)
            self.__speakerBtn.setChecked(False)

    def __on_thread_complete(self):
        self.__speakerBtn.setStyleAndIcon(ICON_SPEAKER)
        self.__speakerBtn.setChecked(False)

    def setText(self, text: str):
        if self.__show_as_markdown:
            self._lbl.setMarkdown(text)
        else:
            self._lbl.setText(text)
        self._lbl.adjustBrowserHeight()

    def addText(self, text: str):
        self._lbl.setText(self._lbl.toPlainText() + text)
        self._lbl.adjustBrowserHeight()
