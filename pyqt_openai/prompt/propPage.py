from qtpy.QtWidgets import QWidget, QLineEdit, QFormLayout
from qtpy.QtCore import Signal


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
        self.__promptPropArr = [{'name': 'Task', 'line_edit': QLineEdit()},
                                {'name': 'Topic', 'line_edit': QLineEdit()},
                                {'name': 'Style', 'line_edit': QLineEdit()},
                                {'name': 'Tone', 'line_edit': QLineEdit()},
                                {'name': 'Audience', 'line_edit': QLineEdit()},
                                {'name': 'Length', 'line_edit': QLineEdit()},
                                {'name': 'Form', 'line_edit': QLineEdit()}]
    def __initUi(self):
        lay = QFormLayout()
        for i in range(len(self.__promptPropArr)):
            lineEdit = self.__promptPropArr[i]['line_edit']
            name = self.__promptPropArr[i]['name']
            lineEdit.setObjectName(name)
            lineEdit.textChanged.connect(self.__textChanged)
            lay.addRow(name, lineEdit)

        self.setLayout(lay)

    def __textChanged(self):
        prompt_text = ''
        for prop in self.__promptPropArr:
            if prop["line_edit"].text().strip():
                prompt_text += f'{prop["name"]}: {prop["line_edit"].text()}\n'
        self.updated.emit(prompt_text)