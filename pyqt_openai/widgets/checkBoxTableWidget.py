from __future__ import annotations

import typing

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QCheckBox, QGridLayout, QHeaderView, QTableWidget, QWidget


class CheckBox(QWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(
        self,
        r_idx: int,
        flag: bool,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.__r_idx: int = r_idx
        self.__initUi(flag)

    def __initUi(
        self,
        flag: bool,
    ):
        chkBox: QCheckBox = QCheckBox()
        chkBox.setChecked(flag)
        chkBox.stateChanged.connect(self.__sendCheckedSignal)

        lay = QGridLayout()
        lay.addWidget(chkBox)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(chkBox, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(lay)

    def __sendCheckedSignal(
        self,
        flag: int,
    ):
        flag: Qt.CheckState = Qt.CheckState(flag)
        self.checkedSignal.emit(self.__r_idx, flag)

    def isChecked(self) -> Qt.CheckState:
        f: bool = self.layout().itemAt(0).widget().isChecked()
        return Qt.CheckState.Checked if f else Qt.CheckState.Unchecked

    def setChecked(
        self,
        f: Qt.CheckState | bool,
    ):
        if isinstance(f, Qt.CheckState):
            self.getCheckBox().setCheckState(f)
        elif isinstance(f, bool):
            self.getCheckBox().setChecked(f)

    def getCheckBox(self) -> QWidget:
        return self.layout().itemAt(0).widget()


class CheckBoxTableWidget(QTableWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        self._default_check_flag: bool = False
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # Least column count (one for checkbox, one for another)
        self.setColumnCount(2)

    def setHorizontalHeaderLabels(
        self,
        labels: typing.Iterable[str],
    ) -> None:
        lst: list[str] = [_ for _ in labels if _]
        lst.insert(0, "")  # 0 index vacant for checkbox
        self.setColumnCount(len(lst))
        super().setHorizontalHeaderLabels(lst)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents,
        )

    def clearContents(
        self,
        start_r_idx: int = 0,
    ):
        for i in range(start_r_idx, self.rowCount()):
            for j in range(1, self.columnCount()):
                self.takeItem(i, j)

    def setDefaultValueOfCheckBox(
        self,
        flag: bool,
    ):
        self._default_check_flag = flag

    def stretchEveryColumnExceptForCheckBox(self):
        if self.horizontalHeader():
            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)

    def insertRow(
        self,
        row: int,
    ) -> None:
        super().insertRow(row)
        self.__setCheckBox(row)

    def setRowCount(self, rows: int) -> None:
        super().setRowCount(rows)
        for row in range(rows):
            self.__setCheckBox(row)

    def __setCheckBox(self, r_idx: int):
        chkBox: CheckBox = CheckBox(r_idx, self._default_check_flag)
        chkBox.checkedSignal.connect(self.__sendCheckedSignal)

        self.setCellWidget(r_idx, 0, chkBox)

        if self._default_check_flag:
            self.checkedSignal.emit(r_idx, Qt.CheckState.Checked)
        self.resizeColumnToContents(0)

    def __sendCheckedSignal(
        self,
        r_idx: int,
        flag: Qt.CheckState,
    ):
        self.checkedSignal.emit(r_idx, flag)

    def toggleState(
        self,
        state: Qt.CheckState | bool,
    ):
        for i in range(self.rowCount()):
            item: QWidget = super().cellWidget(i, 0).getCheckBox()  # pyright: ignore[reportAttributeAccessIssue]
            if not isinstance(item, QCheckBox):
                continue
            item.setChecked(state)  # pyright: ignore[reportArgumentType]

    def getCheckedRows(self):
        return self.__getCheckedStateOfRows(Qt.CheckState.Checked)

    def getUncheckedRows(self):
        return self.__getCheckedStateOfRows(Qt.CheckState.Unchecked)

    def __getCheckedStateOfRows(
        self,
        flag: Qt.CheckState,
    ) -> list[int]:
        flag_lst: list[int] = []
        for i in range(self.rowCount()):
            item: QWidget = super().cellWidget(i, 0)  # pyright: ignore[reportAttributeAccessIssue]
            if item.isChecked() == flag:
                flag_lst.append(i)

        return flag_lst

    def setCheckedAt(
        self,
        idx: int,
        f: bool,
    ):
        self.cellWidget(idx, 0).setChecked(f)  # pyright: ignore[reportAttributeAccessIssue]

    def removeCheckedRows(self):
        self.__removeCertainCheckedStateRows(Qt.CheckState.Checked)

    def removeUncheckedRows(self):
        self.__removeCertainCheckedStateRows(Qt.CheckState.Unchecked)

    def __removeCertainCheckedStateRows(
        self,
        flag: Qt.CheckState,
    ):
        flag_lst: list[int] = self.__getCheckedStateOfRows(flag)
        flag_lst.reverse()
        for i in flag_lst:
            self.removeRow(i)
