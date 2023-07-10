from datetime import datetime

from qtpy.QtGui import QFont
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QListWidget, QDialog, QListWidgetItem, QLabel, QHBoxLayout, QWidget, QApplication, QVBoxLayout

from pyqt_openai.inputDialog import InputDialog
from pyqt_openai.svgButton import SvgButton


class ImageItemWidget(QWidget):
    btnClicked = Signal(QListWidgetItem)
    imageUpdated = Signal(int, str)

    def __init__(self, text: str, item: QListWidgetItem, id):
        super().__init__()
        self.__item = item
        self.__id = id
        self.__initUi(text)

    def __initUi(self, text):
        self.__topicLbl = QLabel(text)

        lay = QVBoxLayout()
        lay.addWidget(self.__topicLbl)
        lay.setContentsMargins(0, 0, 0, 0)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)

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
        lay.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(bottomWidget)

        self.setLayout(lay)

        # Qt bug - not following by app's font size, update the font on its own after setItemWidget being called
        # to avoid BUG (if there is nothing in qt bug report, i'll report by myself)
        # i don't know this was fixed or not in PySide6 so i will check it out FIXME
        self.__topicLbl.setFont(QApplication.font())

        self.setAutoFillBackground(True)

    def text(self):
        return self.__topicLbl.text()

    def enterEvent(self, e):
        self.__btnWidget.setVisible(True)
        return super().enterEvent(e)

    def leaveEvent(self, e):
        self.__btnWidget.setVisible(False)
        return super().leaveEvent(e)

    def __btnClicked(self):
        dialog = InputDialog('Rename', self.__topicLbl.text(), self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            text = dialog.getText()
            self.__topicLbl.setText(text)
            self.imageUpdated.emit(self.__id, text)


class ImageListWidget(QListWidget):
    changed = Signal(QListWidgetItem)
    imageUpdated = Signal(int, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initUi()

    def __initUi(self):
        self.itemClicked.connect(self.__clicked)
        self.currentItemChanged.connect(self.changed)

    def addImage(self, text: str, id: int):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        widget = ImageItemWidget(text, item, id)
        widget.imageUpdated.connect(self.imageUpdated)
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, id)
        self.insertItem(0, item)
        self.setItemWidget(item, widget)

    def __clicked(self, item):
        potentialChkBoxWidgetInItem = QApplication.widgetAt(self.cursor().pos())
        if isinstance(potentialChkBoxWidgetInItem, QWidget) and potentialChkBoxWidgetInItem.children():
            if isinstance(potentialChkBoxWidgetInItem.children()[0], ImageItemWidget):
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

    def getCheckedRowsIds(self):
        return self.__getFlagRows(Qt.Checked, is_id=True)

    def getUncheckedRowsIds(self):
        return self.__getFlagRows(Qt.Unchecked, is_id=True)

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