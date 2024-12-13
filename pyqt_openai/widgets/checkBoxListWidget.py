from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QListWidget, QListWidgetItem

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class CheckBoxListWidget(QListWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.itemChanged.connect(self.__sendCheckedSignal)

    def __sendCheckedSignal(
        self,
        item: QListWidgetItem,
    ):
        r_idx: int = self.row(item)
        state: Qt.CheckState = item.checkState()
        self.checkedSignal.emit(r_idx, state)

    def addItems(
        self,
        items: list[str],
        checked: bool = False,
    ) -> None:
        """Add items to the list widget.
        If checked is True, the items will be checked.
        """
        for item in items:
            self.addItem(item, checked=checked)

    def addItem(
        self,
        item: str | QListWidgetItem,
        checked: bool = False,
    ) -> None:
        if isinstance(item, str):
            item = QListWidgetItem(item)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        if checked:
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)
        super().addItem(item)

    def toggleState(
        self,
        state: Qt.CheckState,
    ):
        for i in range(self.count()):
            item: QListWidgetItem = self.item(i)
            state = Qt.CheckState(state)
            if item.checkState() != state:
                item.setCheckState(state)

    def getCheckedRows(self) -> list[int]:
        return self.__getFlagRows(Qt.CheckState.Checked)

    def getUncheckedRows(self) -> list[int]:
        return self.__getFlagRows(Qt.CheckState.Unchecked)

    def __getFlagRows(
        self,
        flag: Qt.CheckState,
    ) -> list[int]:
        flag_lst: list[int] = []
        for i in range(self.count()):
            item: QListWidgetItem = self.item(i)
            if item.checkState() == flag:
                flag_lst.append(i)

        return flag_lst

    def removeCheckedRows(self):
        self.__removeFlagRows(Qt.CheckState.Checked)

    def removeUncheckedRows(self):
        self.__removeFlagRows(Qt.CheckState.Unchecked)

    def __removeFlagRows(
        self,
        flag: Qt.CheckState,
    ):
        flag_lst = self.__getFlagRows(flag)
        flag_lst = reversed(flag_lst)
        for i in flag_lst:
            self.takeItem(i)

    def getCheckedItems(self) -> list[QListWidgetItem]:
        return [self.item(i) for i in self.getCheckedRows()]

    def getCheckedItemsText(
        self,
        empty_str: str = "",
        include_empty: bool = True,
    ) -> list[str]:
        result: list[str] = [item.text() if item else empty_str for item in self.getCheckedItems()]
        if include_empty:
            return result
        return [text for text in result if text]
