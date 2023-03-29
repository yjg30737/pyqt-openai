from datetime import datetime

from qtpy.QtGui import QFont
from qtpy.QtWidgets import QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QWidget, QApplication, QVBoxLayout


class ConvListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addConv(self, text: str):
        item = QListWidgetItem()
        topicLbl = QLabel(text)

        dateLbl = QLabel()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dateLbl.setText(f'Last updated: {current_time}')
        dateLbl.setFont(QFont('Arial', 9))

        lay = QVBoxLayout()
        lay.addWidget(topicLbl)
        lay.addWidget(dateLbl)

        widget = QWidget()
        widget.setLayout(lay)

        item.setSizeHint(widget.sizeHint())
        self.insertItem(0, item)
        self.setItemWidget(item, widget)
        # Qt bug - not following by app's font size, update the font on its own after setItemWidget being called
        # to avoid BUG (if there is nothing in qt bug report, i'll report by myself)
        # i don't know this was fixed or not in PySide6 so i will check it out FIXME
        topicLbl.setFont(QApplication.font())

    def deleteConv(self):
        item = self.currentItem()
        self.takeItem(self.row(item))

    def clearConv(self):
        for i in range(self.count()-1, -1, -1):
            self.takeItem(i)