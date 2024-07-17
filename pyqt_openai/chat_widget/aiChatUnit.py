import pyperclip
from qtpy.QtCore import Qt
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QLabel, QMessageBox, QWidget, QVBoxLayout, QApplication, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QTextBrowser, QAbstractScrollArea

from pyqt_openai.chat_widget.messageResultDialog import MessageResultDialog
from pyqt_openai.constants import DEFAULT_ICON_SIZE
from pyqt_openai.models import ChatMessageContainer
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.circleProfileImage import RoundedImage


class SourceBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        menuWidget = QWidget()
        lay = QHBoxLayout()

        self.__langLbl = QLabel()
        fnt = self.__langLbl.font()
        fnt.setBold(True)
        self.__langLbl.setFont(fnt)

        copyBtn = Button()
        copyBtn.setStyleAndIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self.__langLbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(copyBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setBackgroundRole(QPalette.ColorRole.Midlight)

        self.__browser = QTextBrowser()
        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__browser)
        lay.setContentsMargins(5, 3, 5, 3)
        lay.setSpacing(0)
        self.setLayout(lay)

    def setText(self, lexer, text):
        self.__langLbl.setText(lexer.name)
        self.__browser.setText(text)
        self.__browser.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

    def getText(self):
        return self.__browser.toPlainText()

    def getLangName(self):
        return self.__langLbl.text().lower()

    def __copy(self):
        pyperclip.copy(self.__browser.toPlainText())


class AIChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__lbl = ''
        self.__plain_text = ''
        self.__find_f = False
        self.__result_info = ''

    def __initUi(self):
        # common
        menuWidget = QWidget()
        lay = QHBoxLayout()

        self.__icon = RoundedImage()
        self.__icon.setMaximumSize(*DEFAULT_ICON_SIZE)

        self.__favoriteBtn = Button()
        self.__favoriteBtn.setStyleAndIcon('ico/favorite_no.svg')
        self.__favoriteBtn.setCheckable(True)
        self.__favoriteBtn.toggled.connect(self.__favorite)

        self.__infoBtn = Button()
        self.__infoBtn.setStyleAndIcon('ico/info.svg')
        self.__infoBtn.clicked.connect(self.__showInfo)

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        self.__copyBtn = Button()
        self.__copyBtn.setStyleAndIcon('ico/copy.svg')
        self.__copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self.__icon)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__favoriteBtn)
        lay.addWidget(self.__infoBtn)
        lay.addWidget(self.__copyBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())

        lay = QVBoxLayout()
        self.__mainWidget = QWidget()
        self.__mainWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase)
        self.setAutoFillBackground(True)

    def __copy(self):
        pyperclip.copy(self.text())

    def __favorite(self, f, insert_f=True):
        favorite = 1 if f else 0
        if favorite:
            self.__favoriteBtn.setStyleAndIcon('ico/favorite_yes.svg')
        else:
            self.__favoriteBtn.setStyleAndIcon('ico/favorite_no.svg')
        if insert_f:
            current_date = DB.updateMessage(self.__result_info.id, favorite)
            self.__result_info.favorite = favorite
            self.__result_info.favorite_set_date = current_date

    def __showInfo(self):
        dialog = MessageResultDialog(self.__result_info)
        dialog.exec()

    def text(self):
        text = ''
        lay = self.__mainWidget.layout()
        for i in range(lay.count()):
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    text += widget.text()
                elif isinstance(widget, SourceBrowser):
                    text += f'```{widget.getLangName()}\n{widget.getText()}```'

        return text

    def alignment(self):
        return Qt.AlignmentFlag.AlignLeft

    def setAlignment(self, a0):
        lay = self.__mainWidget.layout()
        for i in range(lay.count()):
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    widget.setAlignment(a0)

    def disableGUIDuringGenerateResponse(self):
        self.__favoriteBtn.setEnabled(False)
        self.__copyBtn.setEnabled(False)
        self.__infoBtn.setEnabled(False)

    def showConvResultInfo(self, arg: ChatMessageContainer):
        self.__favoriteBtn.setEnabled(True)
        self.__copyBtn.setEnabled(True)
        self.__infoBtn.setEnabled(True)
        self.__result_info = arg
        self.__favorite(True if arg.favorite else False, insert_f=False)

    def setText(self, text: str):
        self.__lbl = QLabel(text)

        self.__lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.__lbl.setWordWrap(True)
        self.__lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.__lbl.setOpenExternalLinks(True)
        self.__lbl.setBackgroundRole(QPalette.ColorRole.AlternateBase)

        self.__mainWidget.layout().addWidget(self.__lbl)

        # old code
        # chunks = text.split('```')
        # for i in range(len(chunks)):
        #     if i % 2 == 0:
        #         lbl = QLabel(chunks[i])
        #
        #         lbl.setAlignment(Qt.AlignLeft)
        #         lbl.setWordWrap(True)
        #         lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #         lbl.setOpenExternalLinks(True)
        #
        #         self.__mainWidget.layout().addWidget(lbl)
        #     else:
        #         browser = SourceBrowser()
        #
        #         lang_name = ''
        #         lang_text = ''
        #
        #         m = re.search('([\S]+)\n*(.+)', chunks[i], re.DOTALL)
        #         if m:
        #             lang_name = m.group(1)
        #             lang_text = m.group(2)
        #         try:
        #             lexer = get_lexer_by_name(lang_name)
        #         except Exception as e:
        #             lexer = get_lexer_by_name('Text')
        #
        #         # get the guessed language based on given code
        #         formatter = HtmlFormatter(style='colorful')
        #
        #         css_styles = formatter.get_style_defs('.highlight')
        #
        #         html_code = f"""
        #         <html>
        #             <head>
        #                 <style>
        #                     {css_styles}
        #                 </style>
        #             </head>
        #             <body>
        #                 {highlight(lang_text, lexer, formatter)}
        #             </body>
        #         </html>
        #         """
        #         browser.setText(lexer, html_code)
        #         self.__mainWidget.layout().addWidget(browser)

    def toPlainText(self):
        return self.__plain_text

    def addText(self, text: str):
        unit = self.__mainWidget.layout().itemAt(self.__mainWidget.layout().count()-1).widget()
        if isinstance(unit, QLabel):
            unit.setText(unit.text()+text)
        elif isinstance(unit, QTextBrowser):
            unit.append(text)

    def getIcon(self):
        return self.__icon.getImage()

    def setIcon(self, filename):
        self.__icon.setImage(filename)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = AIChatUnit()
    w.setText(
        '''
        of course, i can help you!
        ```python
        class ChatUnit(QWidget):
    def __init__(self, user_f=False, parent=None):
        super().__init__(parent)
        self.__initUi(user_f)

    def __initUi(self, user_f):
        # common
        menuWidget = QWidget()
        lay = QHBoxLayout()

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        copyBtn = SvgButton()
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(copyBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        # if chat unit generated by user
        if user_f:
            pass
        # generated by AI
        else:
            pass

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setStyleSheet('QWidget { background-color: #BBB }')

        self.__lbl = QLabel()
        self.__lbl.setStyleSheet('QLabel { padding: 1rem }')

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__lbl)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def __copy(self):
        pyperclip.copy(self.__lbl.text())

    def getLabel(self) -> QLabel:
        return self.__lbl

    def text(self):
        return self.__lbl.text()

    def alignment(self):
        return self.__lbl.alignment()

    def setAlignment(self, a0):
        self.__lbl.setAlignment(a0)

    def setText(self, text: str):
        return self.__lbl.setText(text) 
        ```
        thanks, bye
        '''

    )
    w.show()
    sys.exit(app.exec())