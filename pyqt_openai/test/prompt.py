import sys

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QTableWidget, QTableWidgetItem
from qtpy.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QCompleter
from qtpy.QtCore import Qt
from qtpy.QtGui import QTextCursor

from pyqt_openai.sqlite import SqliteDatabase


class AutoCompleteTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(AutoCompleteTextEdit, self).__init__(parent)
        self.completer = None

    def set_completer(self, completer):
        if self.completer:
            self.completer.activated.disconnect()

        self.completer = completer
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return

        super(AutoCompleteTextEdit, self).keyPressEvent(event)

        if not self.completer:
            return

        if event.key() == Qt.Key_Slash:  # Activate completer when "/" is pressed
            completionPrefix = self.text_under_cursor()

            if completionPrefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(completionPrefix)
                self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(
                0) + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()

    # def keyPressEvent(self, event):
    #     if self.completer and self.completer.popup().isVisible():
    #         if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
    #             event.ignore()
    #             return
    #
    #     isShortcut = (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_E
    #     if not self.completer or not isShortcut:
    #         super(AutoCompleteTextEdit, self).keyPressEvent(event)
    #
    #     ctrlOrShift = event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
    #     if not self.completer or (ctrlOrShift and len(event.text()) == 0):
    #         return
    #
    #     eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="  # end of word characters
    #     hasModifier = (event.modifiers() != Qt.NoModifier) and not ctrlOrShift
    #     completionPrefix = self.text_under_cursor()
    #
    #     if not isShortcut and (hasModifier or len(event.text()) == 0 or len(completionPrefix) < 2 or event.text()[-1] in eow):
    #         self.completer.popup().hide()
    #         return
    #
    #     if completionPrefix != self.completer.completionPrefix():
    #         self.completer.setCompletionPrefix(completionPrefix)
    #         self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
    #
    #     cr = self.cursorRect()
    #     cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
    #     self.completer.complete(cr)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__db = SqliteDatabase()

        self.text_edit = AutoCompleteTextEdit()
        self.init_autocomplete()

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def init_autocomplete(self):
        self.__p_grp = []
        for group in self.__db.selectPropPromptGroup():
            p_grp_attr = [attr for attr in self.__db.selectPropPromptAttribute(group[0])]
            p_grp_value = ''
            for attr_obj in p_grp_attr:
                name = attr_obj[2]
                value = attr_obj[3]
                if value and value.strip():
                    p_grp_value += f'{name}: {value}\n'
            self.__p_grp.append({'name': group[1], 'value': p_grp_value})

        self.__t_grp = [{'name': obj[1], 'value': obj[2]} for obj in self.__db.selectTemplatePrompt()]

        print('Property Group: ', self.__p_grp)
        print('Template: ', self.__t_grp)

        # only name
        p_grp_nm_arr = [obj['name'] for obj in self.__p_grp]
        t_grp_nm_arr = [obj['name'] for obj in self.__t_grp]
        words = p_grp_nm_arr+t_grp_nm_arr

        completer = QCompleter(words)
        completer.activated.connect(self.__activated)
        self.text_edit.set_completer(completer)

    def __activated(self, word):
        for item in self.__p_grp:
            if item['name'] == word:
                v = item['value']
                break
        else:
            # Handle the case when 'b' is not found
            v = ''
        self.text_edit.textCursor().deletePreviousChar()
        self.text_edit.insertPlainText(v)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
