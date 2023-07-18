from qtpy.QtWidgets import QWidget, QComboBox, QTextEdit, QLabel, QVBoxLayout, QApplication, QCheckBox, QFormLayout, \
    QSpinBox, QScrollArea

from pyqt_openai.sqlite import SqliteDatabase


class ImagePage(QScrollArea):
    def __init__(self, db: SqliteDatabase):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db
        self.__info_dict = self.__db.selectInfo(3)

    def __initUi(self):
        modelCmbBox = QComboBox()
        modelCmbBox.addItems(['DALL-E'])
        # modelCmbBox.addItems(['DALL-E', 'Midjourney', 'Stable Diffusion'])
        nSpinBox = QSpinBox()
        nSpinBox.setRange(1, 10)
        nSpinBox.setValue(self.__info_dict['n'])
        nSpinBox.valueChanged.connect(self.__nChanged)
        sizeCmbBox = QComboBox()
        sizeCmbBox.addItems(['256x256', '512x512', '1024x1024'])
        sizeCmbBox.setCurrentText(f"{self.__info_dict['width']}x{self.__info_dict['height']}")
        sizeCmbBox.currentTextChanged.connect(self.__sizeChanged)
        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS['Model'], modelCmbBox)
        lay.addRow(LangClass.TRANSLATIONS['Total'], nSpinBox)
        lay.addRow(LangClass.TRANSLATIONS['Size'], sizeCmbBox)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setWidget(mainWidget)
        self.setWidgetResizable(True)

    def __nChanged(self, v):
        self.__db.updateInfo(3, 'n', v)

    def __sizeChanged(self, v):
        width, height = v.split('x')
        self.__db.updateInfo(3, 'width', width)
        self.__db.updateInfo(3, 'height', height)
