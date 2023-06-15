import inspect
import json

import openai

from qtpy.QtCore import QThread, Signal

from pyqt_openai.apiData import getModelEndpoint


class OpenAIThread(QThread):
    """
    == replyGenerated Signal ==
    First: response
    Second: user or AI
    Third: streaming a chat completion or not
    """
    replyGenerated = Signal(str, bool, bool)
    streamFinished = Signal()

    def __init__(self, model, openai_arg, remember_f, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__model = model
        print(model)
        self.__endpoint = getModelEndpoint(model)
        self.__openai_arg = openai_arg
        self.__remember_f = remember_f

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
            elif self.__endpoint == '/v1/completions':
                openai_object = openai.Completion.create(
                    **self.__openai_arg
                )

                response_text = openai_object['choices'][0]['text'].strip()

                # this doesn't store any data, so we manually do that every time
                if self.__remember_f:
                    conv = {
                        'prompt': self.__openai_arg['prompt'],
                        'response': response_text,
                    }

                    with open('conv.json', 'a') as f:
                        f.write(json.dumps(conv) + '\n')

                self.replyGenerated.emit(response_text, False, False)
        except openai.error.InvalidRequestError as e:
            print(e)
            self.replyGenerated.emit(f'<p style="color:red">{e}</p>', False, False)
        except openai.error.RateLimitError as e:
            self.replyGenerated.emit(f'<p style="color:red">{e}<br/>Check the usage: https://platform.openai.com/account/usage<br/>Update to paid account: https://platform.openai.com/account/billing/overview', False, False)