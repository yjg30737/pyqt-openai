from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QTextDocument
from PyQt5.QtWidgets import QWidget, QTextBrowser, QLabel, \
    QHBoxLayout, QGridLayout, QLineEdit, QMessageBox

from pyqt_openai.chat_widget.chatBrowser import ChatBrowser
from pyqt_openai.svgButton import SvgButton


class FindTextWidget(QWidget):

    prevClicked = pyqtSignal(str)
    nextClicked = pyqtSignal(str)
    closeSignal = pyqtSignal()

    def __init__(self, chatBrowser: ChatBrowser):
        super().__init__()
        self.__chatBrowser = chatBrowser

        self.__selectionsInit()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__selections = []
        self.__cur_idx = 0

    def __initUi(self):
        self.__findTextLineEdit = QLineEdit()
        self.__findTextLineEdit.setStyleSheet('QLineEdit { border: none; }')
        self.__findTextLineEdit.textChanged.connect(self.__textChanged)
        self.__findTextLineEdit.returnPressed.connect(self.next)
        self.setFocusProxy(self.__findTextLineEdit)

        self.__cnt_init_text = '{0} results'
        self.__cnt_cur_idx_text = '{0}/{1}'
        self.__cnt_lbl = QLabel(self.__cnt_init_text.format(0))

        self.__prevBtn = SvgButton()
        self.__prevBtn.setIcon('ico/prev.svg')
        self.__prevBtn.setShortcut('Ctrl+Shift+D')

        self.__nextBtn = SvgButton()
        self.__nextBtn.setShortcut('Enter')
        self.__nextBtn.setIcon('ico/next.svg')
        self.__nextBtn.setShortcut('Ctrl+D')

        self.__prevBtn.clicked.connect(self.prev)
        self.__nextBtn.clicked.connect(self.next)

        self.__btnToggled(False)

        self.__caseBtn = SvgButton()
        self.__caseBtn.setCheckable(True)
        self.__caseBtn.toggled.connect(self.__caseToggled)
        self.__caseBtn.setIcon('ico/case.svg')

        self.__wordBtn = SvgButton()
        self.__wordBtn.setCheckable(True)
        self.__wordBtn.toggled.connect(self.__wordToggled)
        self.__wordBtn.setIcon('ico/word.svg')

        self.__regexBtn = SvgButton()
        self.__regexBtn.setCheckable(True)
        self.__regexBtn.setIcon('ico/regex.svg')

        self.__closeBtn = SvgButton()
        self.__closeBtn.setVisible(False)
        self.__closeBtn.clicked.connect(self.close)
        self.__closeBtn.setShortcut('Escape')
        self.__closeBtn.setIcon('ico/close.svg')

        self.__prevBtn.setToolTip('Previous Occurrence')
        self.__nextBtn.setToolTip('Next Occurrence')
        self.__caseBtn.setToolTip('Match Case')
        self.__wordBtn.setToolTip('Match Word')
        self.__regexBtn.setToolTip('Regex')
        self.__closeBtn.setToolTip('Close')

        lay = QHBoxLayout()
        lay.addWidget(self.__findTextLineEdit)
        lay.addWidget(self.__cnt_lbl)
        lay.addWidget(self.__prevBtn)
        lay.addWidget(self.__nextBtn)
        lay.addWidget(self.__caseBtn)
        lay.addWidget(self.__wordBtn)
        lay.addWidget(self.__regexBtn)
        lay.addWidget(self.__closeBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        lay = QGridLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def widgetTextChanged(self):
        self.__textChanged(self.__findTextLineEdit.text())

    def __textChanged(self, text):
        f1 = text.strip() != ''
        self.__cur_idx = 0
        if f1:
            self.__selections = self.__chatBrowser.setCurrentLabelIncludingTextBySliderPosition(text)
            self.__setCount()
            f2 = len(self.__selections) > 0
            self.__btnToggled(f2)
        else:
            self.__btnToggled(False)


        # flags = 0
        # if self.__caseBtn.isChecked():
        #     flags = flags | QTextDocument.FindCaseSensitively
        # else:
        #     flags = flags & ~QTextDocument.FindCaseSensitively
        # if self.__wordBtn.isChecked():
        #     flags = flags | QTextDocument.FindWholeWords
        # else:
        #     flags = flags & ~QTextDocument.FindWholeWords
        # self.__findInit(text, flags=flags, widgetTextChanged=widgetTextChanged)
        # f2 = len(self.__selections) > 0
        # self.__btnToggled(f1 and f2)

    def __setCount(self):
        word_cnt = len(self.__selections)
        self.__cnt_lbl.setText(self.__cnt_init_text.format(word_cnt))

    def __btnToggled(self, f):
        self.__prevBtn.setEnabled(f)
        self.__nextBtn.setEnabled(f)

    def __selectionsInit(self):
        self.__selections = []
        self.__selections_idx = -1

    def __findInit(self, text, flags=0, widgetTextChanged=False):
        pass
        # def addSelection():
        #     sel = QTextBrowser.ExtraSelection()
        #     sel.cursor = cur
        #     sel.format = fmt
        #     self.__selections.append(sel)
        #
        # self.__selectionsInit()
        # doc = self.__chatBrowser.document()
        # fmt = QTextCharFormat()
        # fmt.setForeground(Qt.green)
        # fmt.setBackground(Qt.darkYellow)
        # cur = QTextCursor()
        # while True:
        #     if flags:
        #         cur = doc.find(text, cur, flags)
        #     else:
        #         cur = doc.find(text, cur)
        #     if cur.isNull() or cur.atEnd():
        #         if cur.atEnd():
        #             if cur.selectedText() == text:
        #                 addSelection()
        #         break
        #     addSelection()
        # self.__chatBrowser.setExtraSelections(self.__selections)
        # self.__setCount()
        # if widgetTextChanged:
        #     pass
        # else:
        #     self.next()

    def __setCurrentPosition(self):
        self.__chatBrowser.verticalScrollBar().setSliderPosition(self.__selections[self.__cur_idx]['pos'])

    def prev(self):
        self.__cur_idx = max(0, self.__cur_idx-1)
        self.__setCurrentPosition()
        # cur_pos = self.__chatBrowser.textCursor().position()
        # text = self.__findTextLineEdit.text()
        #
        # def getPosList():
        #     pos_lst = [selection.cursor.position() for selection in self.__selections]
        #     pos_lst = [c for c in pos_lst if c < cur_pos]
        #     return pos_lst
        #
        # if self.__selections_idx-1 < 0:
        #     if cur_pos > self.__selections[0].cursor.position():
        #         pos_lst = getPosList()
        #         if len(pos_lst) > 0:
        #             closest_value = max(pos_lst)
        #             self.__selections_idx = pos_lst.index(closest_value)
        #             self.__setCursor()
        #             self.__cnt_lbl.setText(self.__cnt_cur_idx_text.format(self.__selections_idx+1, len(self.__selections)))
        #             self.prevClicked.emit(text)
        #         else:
        #             pass
        #     else:
        #         QMessageBox.information(self, 'Notice', 'Start of file.')
        # else:
        #     pos_lst = getPosList()
        #     if len(pos_lst) > 0:
        #         closest_value = max(pos_lst)
        #         if cur_pos in pos_lst:
        #             self.__selections_idx -= 1
        #         else:
        #             self.__selections_idx = pos_lst.index(closest_value)
        #         self.__setCursor()
        #         self.__cnt_lbl.setText(self.__cnt_cur_idx_text.format(self.__selections_idx+1, len(self.__selections)))
        #         self.prevClicked.emit(text)
        #     else:
        #         pass

    def next(self):
        self.__cur_idx = min(len(self.__selections)-1, self.__cur_idx+1)
        self.__setCurrentPosition()
        # cur_pos = self.__chatBrowser.textCursor().position()
        # text = self.__findTextLineEdit.text()
        #
        # def getPosList():
        #     pos_lst = [selection.cursor.position() for selection in self.__selections]
        #     pos_lst = [c for c in pos_lst if c > cur_pos]
        #     return pos_lst
        #
        # if len(self.__selections) > 0:
        #     if self.__selections_idx+1 >= len(self.__selections):
        #         if cur_pos < self.__selections[-1].cursor.position():
        #             pos_lst = getPosList()
        #             if len(pos_lst) > 0:
        #                 closest_value = min(pos_lst)
        #                 self.__selections_idx = len(self.__selections)-len(pos_lst) + pos_lst.index(closest_value)
        #
        #                 self.__setCursor()
        #                 self.__cnt_lbl.setText(
        #                     self.__cnt_cur_idx_text.format(self.__selections_idx + 1, len(self.__selections)))
        #                 self.nextClicked.emit(text)
        #             else:
        #                 pass
        #         else:
        #             QMessageBox.information(self, 'Notice', 'End of file.')
        #     else:
        #         pos_lst = getPosList()
        #         if len(pos_lst) > 0:
        #             closest_value = min(pos_lst)
        #             if cur_pos in pos_lst:
        #                 self.__selections_idx += 1
        #             else:
        #                 self.__selections_idx = len(self.__selections)-len(pos_lst) + pos_lst.index(closest_value)
        #             self.__setCursor()
        #             self.__cnt_lbl.setText(self.__cnt_cur_idx_text.format(self.__selections_idx+1, len(self.__selections)))
        #             self.nextClicked.emit(text)
        #         else:
        #             self.__selections_idx += 1
        #             self.__setCursor()
        #             self.nextClicked.emit(text)

    def __setCursor(self):
        pass
        # cur = self.__selections[self.__selections_idx].cursor
        # start = cur.selectionStart()
        # end = cur.selectionEnd()
        # cur.setPosition(start, QTextCursor.MoveAnchor)
        # cur.setPosition(end, QTextCursor.KeepAnchor)
        #
        # self.__chatBrowser.setTextCursor(cur)
        # self.__chatBrowser.ensureCursorVisible()

    def __caseToggled(self, f):
        text = self.__findTextLineEdit.text()
        self.__textChanged(text)

    def __wordToggled(self, f):
        text = self.__findTextLineEdit.text()
        self.__textChanged(text)

    def showEvent(self, e):
        # cur = self.__chatBrowser.textCursor()
        # text = cur.selectedText()
        # prev_text = self.__findTextLineEdit.text()
        # if prev_text == text:
        #     self.__textChanged(text)
        # else:
        #     self.__findTextLineEdit.setText(text)

        return super().showEvent(e)

    def setCloseBtn(self, f: bool):
        self.__closeBtn.setVisible(f)

    def close(self):
        super().close()
        pass
        # not_selections = []
        # fmt = QTextCharFormat()
        # fmt.setForeground(self.__chatBrowser.textColor())
        # for selection in self.__selections:
        #     cur = selection.cursor
        #     sel = QTextBrowser.ExtraSelection()
        #     sel.cursor = cur
        #     sel.format = fmt
        #     not_selections.append(sel)
        # self.__chatBrowser.setExtraSelections(not_selections)

        self.closeSignal.emit()

    def getLineEdit(self):
        return self.__findTextLineEdit

    def setLineEdit(self, text: str):
        self.__findTextLineEdit.setText(text)
