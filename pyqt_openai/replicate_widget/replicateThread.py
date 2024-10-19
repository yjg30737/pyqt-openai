from PySide6.QtCore import QThread, Signal

from pyqt_openai.globals import REPLICATE_CLIENT
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.util.script import generate_random_prompt


class ReplicateThread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    # TODO remove model as far as possible
    def __init__(
        self, input_args, number_of_images, model, randomizing_prompt_source_arr=None
    ):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        self.__randomizing_prompt_source_arr = randomizing_prompt_source_arr

        self.__number_of_images = number_of_images
        self.__model = model

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            for _ in range(self.__number_of_images):
                if self.__stop:
                    break
                if self.__randomizing_prompt_source_arr is not None:
                    self.__input_args["prompt"] = generate_random_prompt(
                        self.__randomizing_prompt_source_arr
                    )
                result = REPLICATE_CLIENT.get_image_response(
                    model=self.__model, input_args=self.__input_args
                )
                self.replyGenerated.emit(result)
            self.allReplyGenerated.emit()
        except Exception as e:
            self.errorGenerated.emit(str(e))
