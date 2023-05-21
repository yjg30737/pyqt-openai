import pyperclip

from qtpy.QtWidgets import QTextBrowser, QSplitter, QWidget, QLabel, QVBoxLayout, QPushButton, QTabWidget, QScrollArea
from qtpy.QtCore import Qt

from pyqt_openai.prompt.propPage import PropPage
from pyqt_openai.prompt.templatePage import TemplatePage
from pyqt_openai.sqlite import SqliteDatabase


class PromptGeneratorWidget(QScrollArea):
    def __init__(self, db: SqliteDatabase):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db

    def __initUi(self):
        propmtLbl = QLabel('Prompt')

        propPage = PropPage(self.__db)
        propPage.updated.connect(self.__textChanged)

        templatePage = TemplatePage(self.__db)
        templatePage.updated.connect(self.__textChanged)

        self.__prompt = QTextBrowser()
        self.__prompt.setPlaceholderText('Generated Prompt')

        promptTabWidget = QTabWidget()
        promptTabWidget.addTab(propPage, 'Property')
        promptTabWidget.addTab(templatePage, 'Template')

        previewLbl = QLabel('Preview')

        copyBtn = QPushButton('Copy')
        copyBtn.clicked.connect(self.__copy)

        lay = QVBoxLayout()
        lay.addWidget(propmtLbl)
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
        mainSplitter.setOrientation(Qt.Vertical)
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