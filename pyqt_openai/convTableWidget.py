from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QTableWidget, QDialog, QTableWidgetItem, QLabel, QHBoxLayout, QWidget, QApplication, QVBoxLayout

from pyqt_openai.widgets.inputDialog import InputDialog
from pyqt_openai.widgets.svgButton import SvgButton


class ConvTableWidget(QTableWidget):
    changed = Signal(QTableWidgetItem)
    checked = Signal(list)
    convUpdated = Signal(int, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initUi()

    def __initUi(self):
        self.itemClicked.connect(self.__clicked)
        self.currentItemChanged.connect(self.changed)
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['Conversation'])
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()

    def addConv(self, text: str, id: int):
        self.insertRow(0)
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, id)
        self.setItem(0, 0, item)

    def __clicked(self, item):
        if item.column() == 0:
            self.checked.emit(self.getCheckedRowsIds())
        else:
            self.convUpdated.emit(item.data(Qt.UserRole), item.text())

    def toggleState(self, state):
        for i in range(self.rowCount()):
            item = self.item(i, 0)
            if item:
                state = Qt.CheckState(state)
                if item.checkState() != state:
                    item.setCheckState(state)

    def getCheckedRowsIds(self):
        return self.__getFlagRows(Qt.Checked, is_id=True)

    def getUncheckedRowsIds(self):
        return self.__getFlagRows(Qt.Unchecked, is_id=True)

    def __getFlagRows(self, flag: Qt.CheckState, is_id: bool = False):
        flag_lst = []
        for i in range(self.rowCount()):
            item = self.item(i, 0)
            if item:
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
            self.removeRow(i)