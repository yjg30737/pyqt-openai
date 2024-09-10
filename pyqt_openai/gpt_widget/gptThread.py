import openai
from llama_index.core.base.response.schema import StreamingResponse
from PySide6.QtCore import QThread, Signal

from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.pyqt_openai_data import form_response


class GPTThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: streaming or not streaming
    Third: ChatMessageContainer
    """
    replyGenerated = Signal(str, bool, ChatMessageContainer)
    streamFinished = Signal(ChatMessageContainer)

    def __init__(self, input_args, info: ChatMessageContainer):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        self.__info = info
        self.__info.role = 'assistant'

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            response = OPENAI_STRUCT.chat.completions.create(
                **self.__input_args
            )

            if isinstance(response, openai.Stream):
                for chunk in response:
                    if self.__stop:
                        self.__info.finish_reason = 'stopped by user'
                        self.streamFinished.emit(self.__info)
                        break
                    else:
                        response_text = chunk.choices[0].delta.content
                        finish_reason = chunk.choices[0].finish_reason
                        if finish_reason == 'length':
                            self.streamFinished.emit(self.__info)
                        else:
                            if response_text:
                                self.replyGenerated.emit(response_text, True, self.__info)
                            else:
                                if finish_reason == 'stop':
                                    self.__info.finish_reason = chunk.choices[0].finish_reason
                                    self.streamFinished.emit(self.__info)
            else:
                self.__info = form_response(response, self.__info)
                self.replyGenerated.emit(self.__info.content, False, self.__info)
        except Exception as e:
            self.__info.finish_reason = 'Error'
            self.__info.content = f'<p style="color:red">{e}</p>'
            self.replyGenerated.emit(self.__info.content, False, self.__info)


class LlamaOpenAIThread(QThread):
    replyGenerated = Signal(str, bool, ChatMessageContainer)
    streamFinished = Signal(ChatMessageContainer)

    def __init__(self, input_args, info: ChatMessageContainer, wrapper, query_text):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        self.__info = info
        self.__info.role = 'assistant'

        self.__wrapper = wrapper
        self.__query_text = query_text

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            resp = self.__wrapper.get_response(self.__query_text)
            f = isinstance(resp, StreamingResponse)
            if f:
                for response_text in resp.response_gen:
                    if self.__stop:
                        self.__info.finish_reason = 'stopped by user'
                        break
                    else:
                        self.replyGenerated.emit(response_text, True, self.__info)
                self.streamFinished.emit(self.__info)
            else:
                self.__info.content = resp.response
                self.replyGenerated.emit(self.__info.content, False, self.__info)
        except Exception as e:
            self.__info.finish_reason = 'Error'
            self.__info.content = f'<p style="color:red">{e}</p>'
            self.replyGenerated.emit(self.__info.content, False, self.__info)