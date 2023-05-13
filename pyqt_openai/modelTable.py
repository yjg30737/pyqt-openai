from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView
from qtpy.QtCore import Qt


class ModelTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setColumnCount(2)
        self.setRowCount(10)
        self.resizeColumnsToContents()
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        item1 = QTableWidgetItem('Allow Fine Tuning')
        item1.setTextAlignment(Qt.AlignCenter)
        item1.setBackground(QBrush(QColor(230, 230, 230)))
        item2 = QTableWidgetItem('N/A')
        item2.setTextAlignment(Qt.AlignCenter)
        self.setItem(0, 0, item1)
        self.setItem(0, 1, item2)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # TODO set more attributes
    # currently set the allow_fine_tuning only
    def setModelInfo(self, model_list, model_name, prop):
        token = [model['permission'][0][prop] for model in model_list if model['id'] == model_name]
        # check the desired prop exists
        if len(token) > 0:
            token = token[0]
        else:
            token = 'N/A'
        if isinstance(token, bool):
            token = 'Yes' if token else 'No'
        item = QTableWidgetItem(token)
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(0, 1, item)

    # currently get the allow_fine_tuning only
    def getModelInfo(self):
        token = self.item(0, 1).text()
        if token in ['Yes', 'No', 'N/A']:
            token = True if token == 'Yes' else False
        return token