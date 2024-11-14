from PySide6.QtCore import QThread, Signal

from pyqt_openai import G4F_PROVIDER_DEFAULT
from pyqt_openai.globals import G4F_CLIENT
from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.util.replicate import download_image_as_base64
from pyqt_openai.util.common import generate_random_prompt, convert_to_provider


class G4FImageThread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    def __init__(
        self, input_args, number_of_images, randomizing_prompt_source_arr=None
    ):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        self.__randomizing_prompt_source_arr = randomizing_prompt_source_arr

        self.__number_of_images = number_of_images

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            provider = G4F_PROVIDER_DEFAULT
            if self.__input_args["provider"] != G4F_PROVIDER_DEFAULT:
                provider = self.__input_args["provider"]
                self.__input_args["provider"] = convert_to_provider(
                    self.__input_args["provider"]
                )

            for _ in range(self.__number_of_images):
                if self.__stop:
                    break
                if self.__randomizing_prompt_source_arr is not None:
                    self.__input_args["prompt"] = generate_random_prompt(
                        self.__randomizing_prompt_source_arr
                    )
                images = G4F_CLIENT.images
                if provider != G4F_PROVIDER_DEFAULT:
                    images.provider = self.__input_args["provider"]
                else:
                    del self.__input_args["provider"]
                response = images.generate(**self.__input_args)
                arg = {
                    **self.__input_args,
                    "provider": provider,
                    "data": download_image_as_base64(response.data[0].url),
                }

                result = ImagePromptContainer(**arg)
                self.replyGenerated.emit(result)
            self.allReplyGenerated.emit()
        except Exception as e:
            self.errorGenerated.emit(str(e))
