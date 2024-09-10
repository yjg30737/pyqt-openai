from PySide6.QtCore import QThread, Signal

from pyqt_openai.models import ImagePromptContainer


class ReplicateThread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    def __init__(self, input_args, number_of_images, wrapper, model):
        super().__init__()
        self.__input_args = input_args
        self.__stop = False

        self.__number_of_images = number_of_images

        self.__wrapper = wrapper
        self.__model = model

    def stop(self):
        self.__stop = True

    def run(self):
        try:
            for _ in range(self.__number_of_images):
                if self.__stop:
                    break
                result = self.__wrapper.get_image_response(model=self.__model, input_args=self.__input_args)
                self.replyGenerated.emit(result)
            self.allReplyGenerated.emit()
        except Exception as e:
            self.errorGenerated.emit(str(e))
