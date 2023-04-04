from datetime import datetime
import json

from qtpy.QtGui import QFont
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QListWidget, QDialog, QListWidgetItem, QLabel, QHBoxLayout, QWidget, QApplication, QVBoxLayout

from pyqt_openai.inputDialog import InputDialog
from pyqt_openai.svgButton import SvgButton


class ConvItemWidget(QWidget):
    btnClicked = Signal(QListWidgetItem)

    def __init__(self, text: str, item: QListWidgetItem):
        super().__init__()
        self.__item = item
        self.__initUi(text)

    def __initUi(self, text):
        self.__topicLbl = QLabel(text)

        self.__dateLbl = QLabel()
        self.__dateLbl.setFont(QFont('Arial', 9))
        self.__refreshTime()

        lay = QVBoxLayout()
        lay.addWidget(self.__topicLbl)
        lay.addWidget(self.__dateLbl)
        lay.setContentsMargins(0, 0, 0, 0)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        editButton = SvgButton()
        editButton.setIcon('ico/edit.svg')
        editButton.setToolTip('Rename')
        editButton.clicked.connect(self.__btnClicked)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(editButton)
        self.__btnWidget = QWidget()
        self.__btnWidget.setLayout(lay)
        self.__btnWidget.setVisible(False)

        lay = QVBoxLayout()
        lay.addWidget(self.__btnWidget)
        lay.setAlignment(Qt.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(leftWidget)
        lay.addWidget(rightWidget)

        self.setLayout(lay)

        # Qt bug - not following by app's font size, update the font on its own after setItemWidget being called
        # to avoid BUG (if there is nothing in qt bug report, i'll report by myself)
        # i don't know this was fixed or not in PySide6 so i will check it out FIXME
        self.__topicLbl.setFont(QApplication.font())

    def text(self):
        return self.__topicLbl.text()

    def enterEvent(self, e):
        self.__btnWidget.setVisible(True)
        return super().enterEvent(e)

    def leaveEvent(self, e):
        self.__btnWidget.setVisible(False)
        return super().leaveEvent(e)

    def __btnClicked(self):
        dialog = InputDialog('Rename', self.__topicLbl.text())
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            text = dialog.getText()
            self.__topicLbl.setText(text)
            self.__refreshTime()

    def __refreshTime(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__dateLbl.setText(f'Last updated: {current_time}')


class ConvListWidget(QListWidget):
    changed = Signal(QListWidgetItem)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initUi()

    def __initUi(self):
        self.itemClicked.connect(self.__clicked)
        self.currentItemChanged.connect(self.changed)

    def addConv(self, text: str, id: int):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        widget = ConvItemWidget(text, item)
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, id)
        self.insertItem(0, item)
        self.setItemWidget(item, widget)

    def __clicked(self, item):
        if item.listWidget().itemWidget(item) != None:
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
    
    def toggleState(self, state):
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() != state:
                item.setCheckState(state)

    # TODO refactoring getCheckedRows, getCheckedRowsIds, getUncheckedRows
    def getCheckedRows(self):
        return self.__getFlagRows(Qt.Checked)

    def getCheckedRowsIds(self):
        return self.__getFlagRows(Qt.Checked, is_id=True)

    def getUncheckedRows(self):
        return self.__getFlagRows(Qt.Unchecked)

    def __getFlagRows(self, flag: Qt.CheckState, is_id: bool = False):
        flag_lst = []
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == flag:
                token = item.data(Qt.UserRole) if is_id else i
                flag_lst.append(token)

        return flag_lst

    def removeCheckedRows(self):
        self.__removeFlagRows(Qt.Checked)

    def removeUncheckedRows(self):
        self.__removeFlagRows(Qt.Unchecked)

    def __removeFlagRows(self, flag):
        flag_lst = self.__getFlagRows(flag)
        flag_lst = reversed(flag_lst)
        for i in flag_lst:
            self.takeItem(i)