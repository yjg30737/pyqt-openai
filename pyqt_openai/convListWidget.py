from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QWidget


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
        self.addItem(item)
        self.setItemWidget(item, widget)