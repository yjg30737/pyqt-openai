import pyperclip

from PySide6.QtWidgets import QTextBrowser, QSplitter, QWidget, QLabel, QVBoxLayout, QPushButton, QTabWidget, QScrollArea
from PySide6.QtCore import Qt

from pyqt_openai.gpt_widget.prompt_gen_widget.formPage import FormPage
from pyqt_openai.gpt_widget.prompt_gen_widget.sentencePage import SentencePage
from pyqt_openai.lang.translations import LangClass


class PromptGeneratorWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        promptLbl = QLabel(LangClass.TRANSLATIONS['Prompt'])

        formPage = FormPage()
        formPage.updated.connect(self.__textChanged)

        sentencePage = SentencePage()
        sentencePage.updated.connect(self.__textChanged)

        self.__prompt = QTextBrowser()
        self.__prompt.setPlaceholderText(LangClass.TRANSLATIONS['Generated Prompt'])
        self.__prompt.setAcceptRichText(False)

        promptTabWidget = QTabWidget()
        promptTabWidget.addTab(formPage, LangClass.TRANSLATIONS['Form'])
        promptTabWidget.addTab(sentencePage, LangClass.TRANSLATIONS['Sentence'])

        previewLbl = QLabel(LangClass.TRANSLATIONS['Preview'])

        copyBtn = QPushButton(LangClass.TRANSLATIONS['Copy'])
        copyBtn.clicked.connect(self.__copy)

        lay = QVBoxLayout()
        lay.addWidget(promptLbl)
        lay.addWidget(promptTabWidget)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(previewLbl)
        lay.addWidget(self.__prompt)
        lay.addWidget(copyBtn)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)

        mainSplitter = QSplitter()
        mainSplitter.addWidget(topWidget)
        mainSplitter.addWidget(bottomWidget)
        mainSplitter.setOrientation(Qt.Orientation.Vertical)
        mainSplitter.setChildrenCollapsible(False)
        mainSplitter.setHandleWidth(2)
        mainSplitter.setStyleSheet(
            '''
            QSplitter::handle:vertical
            {
                background: #CCC;
                height: 1px;
            }
            ''')

        self.setWidget(mainSplitter)
        self.setWidgetResizable(True)

        self.setStyleSheet('QScrollArea { border: 0 }')

    def __textChanged(self, prompt_text):
        self.__prompt.clear()
        self.__prompt.setText(prompt_text)

    def __copy(self):
        pyperclip.copy(self.__prompt.toPlainText())