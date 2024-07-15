import typing

from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QHeaderView, QTableWidget, QCheckBox
from qtpy.QtWidgets import QWidget, QGridLayout


class CheckBox(QWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(self, r_idx, flag):
        super().__init__()
        self.__r_idx = r_idx
        self.__initUi(flag)

    def __initUi(self, flag):
        chkBox = QCheckBox()
        chkBox.setChecked(flag)
        chkBox.stateChanged.connect(self.__sendCheckedSignal)

        lay = QGridLayout()
        lay.addWidget(chkBox)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(chkBox, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(lay)

    def __sendCheckedSignal(self, flag):
        flag = Qt.CheckState(flag)
        self.checkedSignal.emit(self.__r_idx, flag)

    def isChecked(self):
        f = self.layout().itemAt(0).widget().isChecked()
        return Qt.CheckState.Checked if f else Qt.CheckState.Unchecked

    def setChecked(self, f):
        if isinstance(f, Qt.CheckState):
            self.getCheckBox().setCheckState(f)
        elif isinstance(f, bool):
            self.getCheckBox().setChecked(f)

    def getCheckBox(self):
        return self.layout().itemAt(0).widget()


class CheckBoxTableWidget(QTableWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(self, parent=None):
        self._default_check_flag = False
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # Least column count (one for checkbox, one for another)
        self.setColumnCount(2)

    def setHorizontalHeaderLabels(self, labels: typing.Iterable[str]) -> None:
        lst = [_ for _ in labels if _]
        lst.insert(0, '') # 0 index vacant for checkbox
        self.setColumnCount(len(lst))
        super().setHorizontalHeaderLabels(lst)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

    def clearContents(self, start_r_idx=0):
        for i in range(start_r_idx, self.rowCount()):
            for j in range(1, self.columnCount()):
                self.takeItem(i, j)

    def setDefaultValueOfCheckBox(self, flag: bool):
        self._default_check_flag = flag

    def stretchEveryColumnExceptForCheckBox(self):
        if self.horizontalHeader():
            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)

    def insertRow(self, row: int) -> None:
        super().insertRow(row)
        self.__setCheckBox(row)

    def setRowCount(self, rows: int) -> None:
        super().setRowCount(rows)
        for row in range(0, rows):
            self.__setCheckBox(row)

    def __setCheckBox(self, r_idx):
        chkBox = CheckBox(r_idx, self._default_check_flag)
        chkBox.checkedSignal.connect(self.__sendCheckedSignal)

        self.setCellWidget(r_idx, 0, chkBox)

        if self._default_check_flag:
            self.checkedSignal.emit(r_idx, Qt.CheckState.Checked)
        self.resizeColumnToContents(0)

    def __sendCheckedSignal(self, r_idx, flag: Qt.CheckState):
        self.checkedSignal.emit(r_idx, flag)

    def toggleState(self, state):
        for i in range(self.rowCount()):
            item = super().cellWidget(i, 0).getCheckBox()
            item.setChecked(state)

    def getCheckedRows(self):
        return self.__getCheckedStateOfRows(Qt.CheckState.Checked)

    def getUncheckedRows(self):
        return self.__getCheckedStateOfRows(Qt.CheckState.Unchecked)

    def __getCheckedStateOfRows(self, flag: Qt.CheckState.Checked):
        flag_lst = []
        for i in range(self.rowCount()):
            item = super().cellWidget(i, 0)
            if item.isChecked() == flag:
                flag_lst.append(i)

        return flag_lst

    def setCheckedAt(self, idx: int, f: bool):
        self.cellWidget(idx, 0).setChecked(f)

    def removeCheckedRows(self):
        self.__removeCertainCheckedStateRows(Qt.CheckState.Checked)

    def removeUncheckedRows(self):
        self.__removeCertainCheckedStateRows(Qt.CheckState.Unchecked)

    def __removeCertainCheckedStateRows(self, flag):
        flag_lst = self.__getCheckedStateOfRows(flag)
        flag_lst = reversed(flag_lst)
        for i in flag_lst:
            self.removeRow(i)