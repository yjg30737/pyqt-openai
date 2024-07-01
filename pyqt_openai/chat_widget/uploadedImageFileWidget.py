from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QAbstractItemView

from pyqt_openai.res.language_dict import LangClass


class UploadedImageFileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        lbl = QLabel('Uploaded Files (Only Images)')
        self.__deleteBtn = QPushButton(LangClass.TRANSLATIONS['Delete'])
        self.__deleteBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(lbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.MinimumExpanding))
        lay.addWidget(self.__deleteBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__listWidget = QListWidget()
        self.__listWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__listWidget)

        self.setLayout(lay)

        self.__toggle()

    def __toggle(self):
        f = self.__listWidget.count() > 0
        self.__deleteBtn.setEnabled(f)
        self.setVisible(f)

    def addFiles(self, filenames):
        self.__listWidget.addItems(filenames)
        self.__toggle()

    def getFiles(self):
        return [self.__listWidget.item(i).text() for i in range(self.__listWidget.count())]

    def __delete(self):
        rows = reversed([self.__listWidget.row(item) for item in self.__listWidget.selectedItems()])
        for r in rows:
            self.__listWidget.takeItem(r)
        self.__toggle()

    def clear(self):
        self.__listWidget.clear()