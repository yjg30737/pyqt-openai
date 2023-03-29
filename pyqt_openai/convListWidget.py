from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QWidget, QApplication


class ConvListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addConv(self, text: str):
        item = QListWidgetItem()
        lbl = QLabel(text)
        lay = QHBoxLayout()
        lay.addWidget(lbl)
        widget = QWidget()
        widget.setLayout(lay)

        item.setSizeHint(widget.sizeHint())
        self.insertItem(0, item)
        self.setItemWidget(item, widget)
        # Qt bug - not following by app's font size, update the font on its own after setItemWidget being called
        # to avoid BUG (if there is nothing in qt bug report, i'll report by myself)
        # i don't know this was fixed or not in PySide6 so i will check it out FIXME
        lbl.setFont(QApplication.font())

    def deleteConv(self):
        item = self.currentItem()
        self.takeItem(self.row(item))

    def clearConv(self):
        for i in range(self.count()-1, -1, -1):
            self.takeItem(i)