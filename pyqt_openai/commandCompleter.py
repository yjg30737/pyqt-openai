from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QTableWidget, QHeaderView, QScrollArea, QStyledItemDelegate, \
    QStyle, QTableWidgetItem


class CommandCompleterTableWidgetDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Check if the item is selected
        if option.state & QStyle.StateFlag.State_Active:
            # Set the background color for selected item
            option.palette.setColor(option.palette.Highlight, Qt.GlobalColor.lightGray)

        # Call the base paint method
        super().paint(painter, option, index)


class CommandCompleterTableWidget(QTableWidget):
    showText = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.setColumnCount(2)

        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.clicked.connect(self.__showText)

        delegate = CommandCompleterTableWidgetDelegate()

        self.setItemDelegate(delegate)

    def searchTexts(self, text):
        matched_texts_lst = []
        for i in range(self.rowCount()):
            widget = self.item(i, 0)
            if widget:
                widget_text = widget.text()
                if text.strip() != '':
                    idx = widget_text.lower().find(text.lower())
                    if idx != -1:
                        matched_texts_lst.append(text)
                        self.showRow(i)
                    else:
                        self.hideRow(i)
                else:
                    self.hideRow(i)
        return len(matched_texts_lst) > 0

    def addPromptCommand(self,  prompt_command_lst: list):
        for prompt_command_unit in prompt_command_lst:
            name = prompt_command_unit['name']
            value = prompt_command_unit['value']

            item1 = QTableWidgetItem()
            item1.setText(name)
            item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            item2 = QTableWidgetItem()
            item2.setText(value)
            item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            row_idx = self.rowCount()
            self.setRowCount(row_idx + 1)
            self.setItem(row_idx, 0, item1)
            self.setItem(row_idx, 1, item2)
            self.hideRow(row_idx)

    def __showText(self, idx):
        widget = self.indexWidget(idx)
        if widget:
            self.showText.emit(widget.text())


class CommandCompleter(QScrollArea):
    showText = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__completerTable = CommandCompleterTableWidget()
        self.__completerTable.showText.connect(self.__showText)

        self.setVisible(False)
        self.setWidgetResizable(True)

        self.setWidget(self.__completerTable)

    def __showText(self, text):
        self.setVisible(False)
        self.showText.emit(text)

    def addPromptCommand(self, prompt_command_lst: list):
        self.__completerTable.addPromptCommand(prompt_command_lst)