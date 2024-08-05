import base64

from qtpy.QtCore import QThread, Signal

from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import OPENAI_STRUCT


class DallEThread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    def __init__(self, openai_arg, number_of_images, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__openai_arg = openai_arg
        self.__number_of_images = number_of_images
        self.__stop = False

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            for _ in range(self.__number_of_images):
                if self.__stop:
                    break

                response = OPENAI_STRUCT.images.generate(
                    **self.__openai_arg
                )
                container = ImagePromptContainer(**self.__openai_arg)
                for _ in response.data:
                    image_data = base64.b64decode(_.b64_json)
                    container.data = image_data
                    container.revised_prompt = _.revised_prompt
                    container.width = self.__openai_arg['size'].split('x')[0]
                    container.height = self.__openai_arg['size'].split('x')[1]
                    self.replyGenerated.emit(container)
            self.allReplyGenerated.emit()
        except Exception as e:
            self.errorGenerated.emit(str(e))
