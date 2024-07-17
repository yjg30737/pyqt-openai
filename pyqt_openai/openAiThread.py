import openai
from qtpy.QtCore import QThread, Signal

from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.pyqt_openai_data import form_response


class OpenAIThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: streaming or not streaming
    Third: ChatMessageContainer
    """
    replyGenerated = Signal(str, bool, ChatMessageContainer)
    streamFinished = Signal(ChatMessageContainer)

    def __init__(self, openai_arg, info: ChatMessageContainer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__openai_arg = openai_arg
        self.__stop_streaming = False

        self.__info = info
        self.__info.role = 'assistant'

    def stop_streaming(self):
        self.__stop_streaming = True

    def run(self):
        try:
            response = OPENAI_STRUCT.chat.completions.create(
                **self.__openai_arg
            )

            if isinstance(response, openai.Stream):
                for chunk in response:
                    if self.__stop_streaming:
                        self.__info.finish_reason = 'stopped by user'
                        self.streamFinished.emit(self.__info)
                        break
                    else:
                        response_text = chunk.choices[0].delta.content
                        finish_reason = chunk.choices[0].finish_reason
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
            self.replyGenerated.emit(f'<p style="color:red">{e}</p>', False, self.__info)


class LlamaOpenAIThread(QThread):
    replyGenerated = Signal(str, bool, ChatMessageContainer)
    streamFinished = Signal(dict)

    def __init__(self, llama_idx_instance, openai_arg, query_text, info: ChatMessageContainer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__llama_idx_instance = llama_idx_instance
        self.__openai_arg = openai_arg
        self.__query_text = query_text
        self.__stop_streaming = False
        self.__info = info
        self.__info.role = 'assistant'

    def stop_streaming(self):
        self.__stop_streaming = True

    def run(self):
        try:
            self.__info.content = self.__llama_idx_instance.get_response(self.__query_text)
            # f = isinstance(resp, StreamingResponse)
            # if f:
            #     for response_text in resp.response_gen:
            #         if self.__stop_streaming:
            #             break
            #         else:
            #             self.__info['finish_reason'] = 'stopped by user'
            #             self.replyGenerated.emit(response_text, False, f, self.__info)
            #     self.streamFinished.emit(self.__info)
            # else:
            self.replyGenerated.emit(self.__info.content, False, self.__info)
        except Exception as e:
            self.__info.finish_reason = 'Error'
            self.replyGenerated.emit(f'<p style="color:red">{e}</p>', False, self.__info)