from qtpy.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QHeaderView, QHBoxLayout, \
    QVBoxLayout, QWidget, QDialog
from qtpy.QtCore import Signal, Qt

from pyqt_openai.inputDialog import InputDialog
from pyqt_openai.svgButton import SvgButton


class PropPage(QWidget):
    """
    benchmarked https://gptforwork.com/tools/prompt-generator
    """
    updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__defaultPromptPropArr = [{'name': 'Task', 'value': ''},
                                       {'name': 'Topic', 'value': ''},
                                       {'name': 'Style', 'value': ''},
                                       {'name': 'Tone', 'value': ''},
                                       {'name': 'Audience', 'value': ''},
                                       {'name': 'Length', 'value': ''},
                                       {'name': 'Form', 'value': ''}]

    def __initUi(self):
        self.__addBtn = SvgButton()
        self.__delBtn = SvgButton()

        self.__addBtn.setIcon('ico/add.svg')
        self.__delBtn.setIcon('ico/delete.svg')

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__table = QTableWidget()
        self.__table.setColumnCount(2)
        self.__table.setRowCount(len(self.__defaultPromptPropArr))
        self.__table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.__table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__table.setHorizontalHeaderLabels(['Name', 'Value'])

        for i in range(len(self.__defaultPromptPropArr)):
            name = self.__defaultPromptPropArr[i]['name']
            value = self.__defaultPromptPropArr[i]['value']
            item1 = QTableWidgetItem(name)
            item2 = QTableWidgetItem(value)

            item1.setTextAlignment(Qt.AlignCenter)
            item2.setTextAlignment(Qt.AlignCenter)

            self.__table.setItem(i, 0, item1)
            self.__table.setItem(i, 1, item2)

        self.__table.itemChanged.connect(self.__itemChanged)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__table)

        self.setLayout(lay)

    def __itemChanged(self, item: QTableWidgetItem):
        if item.column() == 1:
            prompt_text = ''
            for i in range(self.__table.rowCount()):
                if self.__table.item(i, 1).text().strip():
                    prompt_text += f'{self.__table.item(i, 0).text()}: {self.__table.item(i, 1).text()}\n'
            self.updated.emit(prompt_text)

    def __add(self):
        dialog = InputDialog('Name', '')
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            text = dialog.getText()
            self.__table.setRowCount(self.__table.rowCount()+1)
            item1 = QTableWidgetItem(text)
            item1.setTextAlignment(Qt.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 0, item1)

            item2 = QTableWidgetItem('')
            item2.setTextAlignment(Qt.AlignCenter)
            self.__table.setItem(self.__table.rowCount()-1, 1, item2)

    def __delete(self):
        for i in sorted(set([i.row() for i in self.__table.selectedIndexes()]), reverse=True):
            self.__table.removeRow(i)