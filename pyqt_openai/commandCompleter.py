from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTableWidget, QHeaderView, QVBoxLayout, QLineEdit, QScrollArea, QLabel, QStyledItemDelegate, \
    QStyle


class CommandCompleterTableWidgetDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Check if the item is selected
        if option.state & QStyle.State_Active:
            # Set the background color for selected item
            option.palette.setColor(option.palette.Highlight, Qt.lightGray)

        # Call the base paint method
        super().paint(painter, option, index)


class CommandCompleterTableWidget(QTableWidget):
    showText = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowFlags(Qt.ToolTip)
        self.setColumnCount(1)

        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.clicked.connect(self.__showText)

        delegate = CommandCompleterTableWidgetDelegate()

        self.setItemDelegate(delegate)

    def searchTexts(self, text):
        matched_texts_lst = []
        for i in range(self.rowCount()):
            widget = self.cellWidget(i, 0)
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

    def addText(self, text):
        tb = QLabel()
        tb.setText(text)
        tb.setIndent(2)
        # tb.setTextInteractionFlags(Qt.NoTextInteraction)
        row_idx = self.rowCount()
        self.setRowCount(row_idx+1)
        self.setCellWidget(row_idx, 0, tb)
        self.hideRow(row_idx)

    def addTexts(self, texts: list):
        for i in range(len(texts)):
            self.addText(texts[i])

    def __showText(self, idx):
        widget = self.indexWidget(idx)
        if widget:
            self.showText.emit(widget.text())


class CommandCompleter(QScrollArea):
    showText = pyqtSignal(str)

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

    def addTexts(self, texts: list):
        self.__completerTable.addTexts(texts)

    def textChanged(self, text):
        f = self.__completerTable.searchTexts(text)
        self.setVisible(f)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        commandCompleter = CommandCompleter()
        lineEdit = QLineEdit()
        lineEdit.textChanged.connect(commandCompleter.textChanged)
        commandCompleter.addTexts(
            'Alberic Litte,Angalmo,Antus Odiil,Ariela Doran,Arriana Valga,Athragar,Bittneld the Curse-Bringer,Carmen Litte,Casta Scribonia,Chanel,Chorrol Jailor,Chorrol Soldier,City Watch,Dar-Ma,Earana,Emfrid,Estelle Renoit,Eugal Belette,Fighters Guild Porter,Francois Motierre,Gaturn gro-Gonk,Glistel,Gureryne Selvilo,Honditar,Jirolin Doran,Kurz gro-Baroth,Laythe Wavrick,Lazy Kaslowyn,Lum gro-Baroth,Malintus Ancrus,Modryn Oreyn,Nardhil,Nermus the Mooch,Orag gra-Bargol,Orgnolf Hairy-Legs,Orok gro-Ghoth,Otius Loran,Rallus Odiil,Rasheda,Rena Bruiant,Reynald Jemane,Rimalus Bruiant,Seed-Neeus,Talasma,Teekeeus,Valus Odiil,Vilena Donton,Wallace'.split(
                ','))

        commandCompleter.showText.connect(lineEdit.setText)

        lay = QVBoxLayout()
        lay.addWidget(commandCompleter)
        lay.addWidget(lineEdit)
        lay.setAlignment(Qt.AlignBottom)

        self.setLayout(lay)


from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mainWindow = Window()
    mainWindow.show()

    app.exec_()