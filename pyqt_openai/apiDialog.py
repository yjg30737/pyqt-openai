# TODO WILL_BE_IMPLEMENTED AFTER v1.1.0

# from qtpy.QtWidgets import QDialog, QVBoxLayout
#
# from pyqt_openai.apiWidget import ApiWidget
#
#
# class ApiDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.__initVal()
#         self.__initUi()
#
#     def __initVal(self):
#         self.__openAiEnabled = False
#
#     def __initUi(self):
#         # TODO LANGAUGE
#         self.setWindowTitle("API Dialog")
#         self.__openaiApiWidget = ApiWidget(self)
#         self.__openaiApiWidget.onAIEnabled.connect(self.__openAiEnabled)
#
#         lay = QVBoxLayout()
#         lay.addWidget(self.__openaiApiWidget)
#         self.setLayout(lay)
#
#     def getAIEnabled(self):
#         return self.__openAiEnabled
