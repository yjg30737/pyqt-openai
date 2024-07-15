from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QListWidgetItem, QListWidget


class CheckBoxListWidget(QListWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(self):
        super().__init__()
        self.itemChanged.connect(self.__sendCheckedSignal)

    def __sendCheckedSignal(self, item):
        r_idx = self.row(item)
        state = item.checkState()
        self.checkedSignal.emit(r_idx, state)

    def addItems(self, items, checked=False) -> None:
        """
        Add items to the list widget.
        If checked is True, the items will be checked.
        """
        for item in items:
            self.addItem(item, checked=checked)

    def addItem(self, item, checked=False) -> None:
        if isinstance(item, str):
            item = QListWidgetItem(item)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        if checked:
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)
        super().addItem(item)

    def toggleState(self, state):
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() != state:
                item.setCheckState(state)

    def getCheckedRows(self):
        return self.__getFlagRows(Qt.CheckState.Checked)

    def getUncheckedRows(self):
        return self.__getFlagRows(Qt.CheckState.Unchecked)

    def __getFlagRows(self, flag: Qt.CheckState):
        flag_lst = []
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == flag:
                flag_lst.append(i)

        return flag_lst

    def removeCheckedRows(self):
        self.__removeFlagRows(Qt.CheckState.Checked)

    def removeUncheckedRows(self):
        self.__removeFlagRows(Qt.CheckState.Unchecked)

    def __removeFlagRows(self, flag):
        flag_lst = self.__getFlagRows(flag)
        flag_lst = reversed(flag_lst)
        for i in flag_lst:
            self.takeItem(i)

    def getCheckedItems(self):
        return [self.item(i) for i in self.getCheckedRows()]

    def getCheckedItemsText(self, empty_str='', include_empty=True):
        result = [item.text() if item else empty_str for item in self.getCheckedItems()]
        if include_empty:
            return result
        return [text for text in result if text]