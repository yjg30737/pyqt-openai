from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QAbstractItemView
from qtpy.QtWidgets import QWidget, QTableWidget, QVBoxLayout
from qtpy.QtCore import Signal


class TemplatePage(QWidget):
    updated = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        # this template has to be connected with db
        # QSqlTableModel
        self.__templateTable = QTableWidget()
        self.__templateTable.setColumnCount(2)
        self.__templateTable.setHorizontalHeaderLabels(['Content', 'Variables'])
        self.__templateTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.__templateTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__templateTable.currentItemChanged.connect(self.__rowChanged)

        # sample
        # Alex Brogan's prompt example
        sampleTemplateItems = [
            'Identify the 20% of [topic or skill] that will yield 80% of the desired results and provide a focused learning plan to master it.',
            'Explain [topic or skill] in the simplest terms possible as if teaching it to a complete beginner. Identify gaps in my understanding and suggest resources to fill them.',
            'Create a study plan that mixes different topics or skills within [subject area] to help me develop a more robust understanding and facilitate connections between them.',
            'Design a spaced repetition schedule for me to effectively review [topic or skill] over time, ensuring better retention and recall.',
            'Help me create mental models or analogies to better understand and remember key concepts in [topic or skill].',
            'Suggest various learning resources (e.g., videos, books, podcasts, interactive exercises) for [topic or skill] that cater to different learning styles.',
            'Provide me with a series of challenging questions or problems related to [topic or skill] to test my understanding and improve long-term retention.',
            'Transform key concepts or lessons from [topic or skill] into engaging stories or narratives to help me better remember and understand the material.',
            'Design a deliberate practice routine for [topic or skill], focusing on my weaknesses and providing regular feedback for improvement.',
            'Guide me through a visualization exercise to help me internalize [topic or skill] and imagine myself succesfully applying it in real-life situations.'
        ]

        self.__templateTable.setRowCount(len(sampleTemplateItems))
        for i in range(len(sampleTemplateItems)):
            content = sampleTemplateItems[i]
            self.__templateTable.setItem(i, 0, QTableWidgetItem(content))
            # variable = content.find()
            self.__templateTable.setItem(i, 1, QTableWidgetItem('topic or skill'))

        lay = QVBoxLayout()
        lay.addWidget(self.__templateTable)

        self.setLayout(lay)

    def __rowChanged(self, new_item: QTableWidgetItem, old_item: QTableWidgetItem):
        content = self.__templateTable.item(new_item.row(), 0).text() if new_item.column() == 1 else new_item.text()
        variable = self.__templateTable.item(new_item.row(), 1).text()
        self.updated.emit(content, variable)
