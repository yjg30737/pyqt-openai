import openai

from chatWidget import Prompt, ChatBrowser

# this API key should be yours
# openai.api_key = '[MY_OPENAPI_API_KEY]'

from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

QApplication.setFont(QFont('Arial', 12))


class OpenAIThread(QThread):
    replyGenerated = pyqtSignal(str, bool)

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__question = question

    def run(self):
        openai_object = openai.Completion.create(
            engine="text-davinci-003",
            prompt=self.__question,
            temperature=0.5,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        response_text = openai_object['choices'][0]['text'].strip()

        self.replyGenerated.emit(response_text, False)


class OpenAIChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('PyQt OpenAI Chatbot v0.0.1')
        self.__prompt = Prompt()
        self.__lineEdit = self.__prompt.getTextEdit()
        self.__lineEdit.setPlaceholderText('Write some text...')
        self.__lineEdit.returnPressed.connect(self.__chat)
        self.__browser = ChatBrowser()
        lay = QVBoxLayout()
        lay.addWidget(self.__browser)
        lay.addWidget(self.__prompt)
        lay.setSpacing(0)
        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setCentralWidget(mainWidget)
        self.resize(600, 400)

        self.__browser.showText('Hello!', True)
        self.__browser.showText('Hello! How may i help you?', False)

    def __chat(self):
        self.__t = OpenAIThread(self.__lineEdit.toPlainText())
        self.__t.replyGenerated.connect(self.__browser.showText)
        self.__browser.showText(self.__lineEdit.toPlainText(), True)
        self.__lineEdit.clear()
        self.__t.start()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = OpenAIChatBot()
    w.show()
    app.exec()