import base64

from PySide6.QtCore import QThread, Signal

from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT
from pyqt_openai.util.script import generate_random_prompt


class DallEThread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    def __init__(self, input_args, number_of_images, randomizing_prompt_source_arr=None):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        if randomizing_prompt_source_arr is not None:
            self.__randomizing_prompt_source_arr = randomizing_prompt_source_arr

        self.__number_of_images = number_of_images

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            for _ in range(self.__number_of_images):
                if self.__stop:
                    break
                if self.__randomizing_prompt_source_arr is not None:
                    self.__input_args['prompt'] = generate_random_prompt(self.__randomizing_prompt_source_arr)
                response = OPENAI_STRUCT.images.generate(
                    **self.__input_args
                )
                container = ImagePromptContainer(**self.__input_args)
                for _ in response.data:
                    image_data = base64.b64decode(_.b64_json)
                    container.data = image_data
                    container.revised_prompt = _.revised_prompt
                    container.width = self.__input_args['size'].split('x')[0]
                    container.height = self.__input_args['size'].split('x')[1]
                    self.replyGenerated.emit(container)
            self.allReplyGenerated.emit()
        except Exception as e:
            self.errorGenerated.emit(str(e))
