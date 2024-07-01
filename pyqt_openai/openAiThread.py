import inspect
import openai
from PyQt6.QtCore import QThread, Signal

from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.pyqt_openai_data import get_model_endpoint, form_response, get_vision_response, is_gpt_vision


class OpenAIThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: user or AI
    Third: streaming or not streaming
    Forth: Finish reason
    """
    replyGenerated = Signal(str, bool, bool, dict)
    streamFinished = Signal(dict)

    def __init__(self, model, openai_arg, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__endpoint = get_model_endpoint(model)
        self.__openai_arg = openai_arg
        self.__stop_streaming = False

        self.__info_dict = info

    def stop_streaming(self):
        self.__stop_streaming = True

    def run(self):
        try:
            if self.__endpoint == '/v1/chat/completions':
                response = ''
                if openai.__version__ <= str(0.28):
                    response = openai.ChatCompletion.create(
                           **self.__openai_arg
                    )
                    # If it is streaming, type will be generator
                    if inspect.isgenerator(response):
                        for chunk in response:
                            if self.__stop_streaming:
                                self.__info_dict['finish_reason'] = 'stopped by user'
                                self.streamFinished.emit(self.__info_dict)
                                break
                            else:
                                delta = chunk['choices'][0]['delta']
                                response_text = delta.get('content', '')
                                if response_text:
                                    self.replyGenerated.emit(response_text, False, True, self.__info_dict)
                                else:
                                    self.__info_dict['finish_reason'] = chunk['choices'][0].get('finish_reason', '')
                                    self.streamFinished.emit(self.__info_dict)
                    else:
                        response_text, self.__info_dict = form_response(response, self.__info_dict)
                        self.replyGenerated.emit(response_text, False, False, self.__info_dict)
                elif openai.__version__ >= str(1.0):
                    if is_gpt_vision(self.__openai_arg['model']):
                        response_text, self.__info_dict = get_vision_response(self.__openai_arg, self.__info_dict)
                        self.replyGenerated.emit(response_text, False, False, self.__info_dict)
                    else:
                        response = OPENAI_STRUCT.chat.completions.create(
                            **self.__openai_arg
                        )
                        if isinstance(response, openai.Stream):
                            for chunk in response:
                                if self.__stop_streaming:
                                    self.__info_dict['finish_reason'] = 'stopped by user'
                                    self.streamFinished.emit(self.__info_dict)
                                    break
                                else:
                                    response_text = chunk.choices[0].delta.content
                                    if response_text:
                                        self.replyGenerated.emit(response_text, False, True, self.__info_dict)
                                    else:
                                        self.__info_dict['finish_reason'] = chunk.choices[0].finish_reason
                                        self.streamFinished.emit(self.__info_dict)
                        else:
                            response_text, self.__info_dict = form_response(response, self.__info_dict)
                            self.replyGenerated.emit(response_text, False, False, self.__info_dict)
        except Exception as e:
            self.__info_dict['finish_reason'] = 'Error'
            self.replyGenerated.emit(f'<p style="color:red">{e}</p>', False, False, self.__info_dict)


class LlamaOpenAIThread(QThread):
    replyGenerated = Signal(str, bool, bool, dict)
    streamFinished = Signal(dict)

    def __init__(self, llama_idx_instance, openai_arg, query_text, info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__llama_idx_instance = llama_idx_instance
        self.__openai_arg = openai_arg
        self.__query_text = query_text
        self.__stop_streaming = False

        self.__info_dict = info

    def stop_streaming(self):
        self.__stop_streaming = True

    def run(self):
        try:
            resp = self.__llama_idx_instance.get_response(self.__query_text)
            # f = isinstance(resp, StreamingResponse)
            # if f:
            #     for response_text in resp.response_gen:
            #         if self.__stop_streaming:
            #             break
            #         else:
            #             self.__info_dict['finish_reason'] = 'stopped by user'
            #             self.replyGenerated.emit(response_text, False, f, self.__info_dict)
            #     self.streamFinished.emit(self.__info_dict)
            # else:
            self.replyGenerated.emit(resp, False, False, self.__info_dict)
        except Exception as e:
            self.__info_dict['finish_reason'] = 'Error'
            self.replyGenerated.emit(f'<p style="color:red">{e}</p>', False, False, self.__info_dict)