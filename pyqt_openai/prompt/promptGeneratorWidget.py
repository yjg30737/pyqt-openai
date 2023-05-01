import pyperclip

from qtpy.QtWidgets import QApplication, QTextBrowser, QWidget, QTextEdit, QLabel, QVBoxLayout, QLineEdit, \
    QFormLayout, QTableWidget, QPushButton, QTabWidget

from qtpy.QtGui import QTextCursor

from pyqt_openai.prompt.propPage import PropPage
from pyqt_openai.prompt.templatePage import TemplatePage


class PromptGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        propmtLbl = QLabel('Prompt')

        propPage = PropPage()
        propPage.updated.connect(self.__textChanged)

        templatePage = TemplatePage()
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
        lay.addWidget(previewLbl)
        lay.addWidget(self.__prompt)
        lay.addWidget(copyBtn)

        self.setLayout(lay)

    def __textChanged(self, prompt_text):
        self.__prompt.clear()
        self.__prompt.setText(prompt_text)

    def __copy(self):
        pyperclip.copy(self.__prompt.toPlainText())


if __name__ == '__main__':
    app = QApplication([])
    window = PromptGeneratorWidget()
    window.show()
    app.exec_()
