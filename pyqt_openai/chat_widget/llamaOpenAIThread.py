from llama_index.core.base.response.schema import StreamingResponse
from PySide6.QtCore import QThread, Signal

from pyqt_openai.models import ChatMessageContainer


# TODO
# Should combine with ChatThread
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