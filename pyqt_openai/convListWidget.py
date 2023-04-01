from datetime import datetime

from qtpy.QtGui import QFont
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QListWidget, QPushButton, QListWidgetItem, QLabel, QHBoxLayout, QWidget, QApplication, QVBoxLayout


class ConvItemWidget(QWidget):
    def __init__(self, text: str):
        super().__init__()
        self.__initUi(text)

    def __initUi(self, text):
        self.__topicLbl = QLabel(text)

        dateLbl = QLabel()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dateLbl.setText(f'Last updated: {current_time}')
        dateLbl.setFont(QFont('Arial', 9))

        lay = QVBoxLayout()
        lay.addWidget(self.__topicLbl)
        lay.addWidget(dateLbl)
        lay.setContentsMargins(0, 0, 0, 0)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(QPushButton('Edit'))
        self.__btnWidget = QWidget()
        self.__btnWidget.setLayout(lay)
        self.__btnWidget.setVisible(False)

        lay = QVBoxLayout()
        lay.addWidget(self.__btnWidget)
        lay.setAlignment(Qt.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(leftWidget)
        lay.addWidget(rightWidget)

        self.setLayout(lay)

        # Qt bug - not following by app's font size, update the font on its own after setItemWidget being called
        # to avoid BUG (if there is nothing in qt bug report, i'll report by myself)
        # i don't know this was fixed or not in PySide6 so i will check it out FIXME
        self.__topicLbl.setFont(QApplication.font())

    def text(self):
        return self.__topicLbl.text()

    def enterEvent(self, e):
        self.__btnWidget.setVisible(True)
        return super().enterEvent(e)

    def leaveEvent(self, e):
        self.__btnWidget.setVisible(False)
        return super().leaveEvent(e)


class ConvListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initUi()

    def __initUi(self):
        self.itemClicked.connect(self.__clicked)

    def addConv(self, text: str):
        item = QListWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        widget = ConvItemWidget(text)
        item.setSizeHint(widget.sizeHint())
        self.insertItem(0, item)
        self.setItemWidget(item, widget)

    def __clicked(self, item):
        if item.listWidget().itemWidget(item) != None:
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

    def deleteConv(self):
        item = self.currentItem()
        self.takeItem(self.row(item))

    def clearConv(self):
        for i in range(self.count()-1, -1, -1):
            self.takeItem(i)