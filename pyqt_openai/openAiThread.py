import inspect
import json

import openai
from llama_index.response.schema import StreamingResponse

from qtpy.QtCore import QThread, Signal

from pyqt_openai.apiData import getModelEndpoint


class OpenAIThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: user or AI
    Third: streaming or not streaming
    """
    replyGenerated = Signal(str, bool, bool)
    streamFinished = Signal()

    def __init__(self, model, openai_arg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__endpoint = getModelEndpoint(model)
        self.__openai_arg = openai_arg

    def run(self):
        try:
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
                            self.replyGenerated.emit(response_text, False, True)
                        else:
                            finish_reason = chunk['choices'][0].get('finish_reason', '')
                            if finish_reason:
                                self.streamFinished.emit()
                else:
                    response_text = response['choices'][0]['message']['content']
                    self.replyGenerated.emit(response_text, False, False)
        except openai.error.InvalidRequestError as e:
            self.replyGenerated.emit(f'<p style="color:red">{e}</p>', False, False)
        except openai.error.RateLimitError as e:
            self.replyGenerated.emit(f'<p style="color:red">{e}<br/>Check the usage: https://platform.openai.com/account/usage<br/>Update to paid account: https://platform.openai.com/account/billing/overview', False, False)


class LlamaOpenAIThread(QThread):
    replyGenerated = Signal(str, bool, bool)
    streamFinished = Signal()

    def __init__(self, llama_idx_instance, openai_arg, query_text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__llama_idx_instance = llama_idx_instance
        self.__openai_arg = openai_arg
        self.__query_text = query_text

    def run(self):
        try:
            self.__llama_idx_instance.set_openai_arg(**self.__openai_arg)
            resp = self.__llama_idx_instance.get_response(self.__query_text)
            f = isinstance(resp, StreamingResponse)
            if f:
                for response_text in resp.response_gen:
                    self.replyGenerated.emit(response_text, False, f)
                self.streamFinished.emit()
            else:
                self.replyGenerated.emit(resp.response, False, f)
        except openai.error.InvalidRequestError as e:
            self.replyGenerated.emit('<p style="color:red">Your request was rejected as a result of our safety system.<br/>'
                                     'Your prompt may contain text that is not allowed by our safety system.</p>', False)
        except openai.error.RateLimitError as e:
            self.replyGenerated.emit(f'<p style="color:red">{e}<br/>Check the usage: https://platform.openai.com/account/usage<br/>Update to paid account: https://platform.openai.com/account/billing/overview', False)