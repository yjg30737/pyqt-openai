from PySide6.QtCore import QThread, Signal

from pyqt_openai.models import ImagePromptContainer


class ReplicateThread(QThread):
    replyGenerated = Signal(ImagePromptContainer)
    errorGenerated = Signal(str)
    allReplyGenerated = Signal()

    def __init__(self, wrapper, model, input_args, number_of_images):
        super().__init__()
        self.__wrapper = wrapper
        self.__model = model
        self.__input_args = input_args
        self.__number_of_images = number_of_images
        self.__stop = False

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
