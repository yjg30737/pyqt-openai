import re

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QLabel, \
    QHBoxLayout, QGridLayout, QLineEdit, QMessageBox

from pyqt_openai.gpt_widget.center.chatBrowser import ChatBrowser
from pyqt_openai import DEFAULT_SHORTCUT_FIND_PREV, DEFAULT_SHORTCUT_FIND_NEXT, DEFAULT_SHORTCUT_GENERAL_ACTION, DEFAULT_SHORTCUT_FIND_CLOSE, ICON_PREV, \
    ICON_NEXT, ICON_CASE, ICON_WORD, ICON_REGEX, ICON_CLOSE
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.button import Button


class FindTextWidget(QWidget):

    prevClicked = Signal(str)
    nextClicked = Signal(str)
    closeSignal = Signal()

    def __init__(self, chatBrowser: ChatBrowser):
        super().__init__()
        self.__chatBrowser = chatBrowser
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__selections = []
        self.__cur_text = ''
        self.__cur_idx = 0

    def __initUi(self):
        self.__findTextLineEdit = QLineEdit()
        self.__findTextLineEdit.textChanged.connect(self.initFind)
        self.__findTextLineEdit.returnPressed.connect(self.next)
        self.setFocusProxy(self.__findTextLineEdit)

        self.__cnt_init_text = '{0} results'
        self.__cnt_cur_idx_text = '{0}/{1}'
        self.__cnt_lbl = QLabel(self.__cnt_init_text.format(0))

        self.__prevBtn = Button()
        self.__prevBtn.setStyleAndIcon(ICON_PREV)
        self.__prevBtn.setShortcut(DEFAULT_SHORTCUT_FIND_PREV)

        self.__nextBtn = Button()
        self.__nextBtn.setShortcut(DEFAULT_SHORTCUT_GENERAL_ACTION)
        self.__nextBtn.setStyleAndIcon(ICON_NEXT)
        self.__nextBtn.setShortcut(DEFAULT_SHORTCUT_FIND_NEXT)

        self.__prevBtn.clicked.connect(self.prev)
        self.__nextBtn.clicked.connect(self.next)

        self.__btnToggled(False)

        self.__caseBtn = Button()
        self.__caseBtn.setCheckable(True)
        self.__caseBtn.toggled.connect(self.__caseToggled)
        self.__caseBtn.setStyleAndIcon(ICON_CASE)

        self.__wordBtn = Button()
        self.__wordBtn.setCheckable(True)
        self.__wordBtn.toggled.connect(self.__wordToggled)
        self.__wordBtn.setStyleAndIcon(ICON_WORD)

        self.__regexBtn = Button()
        self.__regexBtn.setCheckable(True)
        self.__regexBtn.toggled.connect(self.__regexToggled)
        self.__regexBtn.setStyleAndIcon(ICON_REGEX)

        self.__prevBtn.setToolTip(LangClass.TRANSLATIONS['Previous Occurrence'] + f' ({DEFAULT_SHORTCUT_FIND_PREV})')
        self.__nextBtn.setToolTip(LangClass.TRANSLATIONS['Next Occurrence'] + f' ({DEFAULT_SHORTCUT_FIND_NEXT})')
        self.__caseBtn.setToolTip(LangClass.TRANSLATIONS['Match Case'])
        self.__wordBtn.setToolTip(LangClass.TRANSLATIONS['Match Word'])
        self.__regexBtn.setToolTip(LangClass.TRANSLATIONS['Regex'])

        lay = QHBoxLayout()
        lay.addWidget(self.__findTextLineEdit)
        lay.addWidget(self.__cnt_lbl)
        lay.addWidget(self.__prevBtn)
        lay.addWidget(self.__nextBtn)
        lay.addWidget(self.__caseBtn)
        lay.addWidget(self.__wordBtn)
        lay.addWidget(self.__regexBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        lay = QGridLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    # TODO REFACTORING AFTER v1.0.0
    def __initSelections(self, text):
        # Show "bad pattern" message if text is "\"
        if self.__regexBtn.isChecked() and re.escape(text) == re.escape('\\'):
            QMessageBox.warning(self, LangClass.TRANSLATIONS['Warning'], LangClass.TRANSLATIONS['Bad pattern'])
        else:
            self.__selections = self.__chatBrowser.setCurrentLabelIncludingTextBySliderPosition(text,
                                                                                                case_sensitive=self.__caseBtn.isChecked(),
                                                                                                word_only=self.__wordBtn.isChecked(),
                                                                                                is_regex=self.__regexBtn.isChecked())
            is_exist = len(list(map(lambda x: x['pattern'], self.__selections))) > 0 and text.strip() != ''

            if is_exist:
                self.__setCurrentPosition()
            else:
                self.__chatBrowser.clearFormatting()
            self.__btnToggled(is_exist)

    # TODO REFACTORING AFTER v1.0.0
    def clearFormatting(self):
        self.__chatBrowser.clearFormatting()
        self.__selections = []
        self.__btnToggled(False)
        self.__setCount()

    # TODO REFACTORING AFTER v1.0.0
    def initFind(self, text):
        f1 = text.strip() != ''
        self.__cur_idx = 0
        self.__cur_text = text
        self.__initSelections(text)
        if not f1:
            self.__selections = []
            self.__btnToggled(False)
        self.__setCount()

    def __setCount(self):
        word_cnt = len(self.__selections)
        self.__cnt_lbl.setText(self.__cnt_init_text.format(word_cnt))

    def __btnToggled(self, f):
        self.__prevBtn.setEnabled(f)
        self.__nextBtn.setEnabled(f)

    def __setCurrentPosition(self):
        self.__chatBrowser.highlightText(self.__selections[self.__cur_idx]['class'], self.__selections[self.__cur_idx]['pattern'], self.__caseBtn.isChecked())
        self.__chatBrowser.verticalScrollBar().setSliderPosition(self.__selections[self.__cur_idx]['pos'])

    def prev(self):
        self.__chatBrowser.clearFormatting(self.__selections[self.__cur_idx]['class'])
        self.__cur_idx -= 1
        if self.__cur_idx == -1:
            QMessageBox.information(self, LangClass.TRANSLATIONS['Information'], LangClass.TRANSLATIONS['Reached the beginning'])
            self.__cur_idx = 0
        self.__setCurrentPosition()

    def next(self):
        self.__chatBrowser.clearFormatting(self.__selections[self.__cur_idx]['class'])
        self.__cur_idx += 1
        if self.__cur_idx == len(self.__selections):
            QMessageBox.information(self, LangClass.TRANSLATIONS['Information'], LangClass.TRANSLATIONS['Reached the end'])
            self.__cur_idx = len(self.__selections) - 1
        self.__setCurrentPosition()

    def __caseToggled(self, f):
        text = self.__findTextLineEdit.text()
        self.initFind(text)

    def __wordToggled(self, f):
        text = self.__findTextLineEdit.text()
        self.initFind(text)

    def __regexToggled(self, f):
        # regex and word-only feature can't be use at the same time
        self.__wordBtn.setChecked(False)
        text = self.__findTextLineEdit.text()
        self.initFind(text)

    def getLineEdit(self):
        return self.__findTextLineEdit

    def setLineEdit(self, text: str):
        self.__findTextLineEdit.setText(text)