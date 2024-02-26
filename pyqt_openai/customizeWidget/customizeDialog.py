from qtpy.QtWidgets import QSplitter, QSizePolicy
from qtpy.QtCore import Qt, QSettings
from qtpy.QtWidgets import QDialog, QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFormLayout

from pyqt_openai.circleProfileImage import RoundedImage
from pyqt_openai.customizeWidget.themeWidget import ThemeWidget
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.widgets.imageView import ImageView


class CustomizeDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('../pyqt_openai.ini', QSettings.IniFormat)

        if not self.__settings_ini.contains('background_image'):
            self.__settings_ini.setValue('background_image', '')
        if not self.__settings_ini.contains('user_image'):
            self.__settings_ini.setValue('user_image', 'ico/user.svg')
        if not self.__settings_ini.contains('ai_image'):
            self.__settings_ini.setValue('ai_image', 'ico/openai.svg')
        if not self.__settings_ini.contains('theme_color'):
            self.__settings_ini.setValue('theme_color', 'ico/openai.svg')
        if not self.__settings_ini.contains('theme_font'):
            self.__settings_ini.setValue('theme_font', 'ico/openai.svg')

        self.__background_image = self.__settings_ini.value('background_image', type=str)
        self.__user_image = self.__settings_ini.value('user_image', type=str)
        self.__ai_image = self.__settings_ini.value('ai_image', type=str)
        self.__theme_color = self.__settings_ini.value('color', type=str)
        self.__theme_font = self.__settings_ini.value('font', type=str)

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['Customize (working)'])
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self.__homePageGraphicsView = ImageView()
        self.__homePageGraphicsView.setFilename(self.__background_image)

        self.__userImage = RoundedImage()
        self.__userImage.setMaximumSize(24, 24)
        self.__userImage.setImage(self.__user_image)
        self.__AIImage = RoundedImage()
        self.__AIImage.setImage(self.__ai_image)
        self.__AIImage.setMaximumSize(24, 24)

        self.__findPathWidget1 = FindPathWidget()
        self.__findPathWidget1.getLineEdit().setText(self.__background_image)
        self.__findPathWidget1.added.connect(self.__homePageGraphicsView.setFilename)
        self.__findPathWidget2 = FindPathWidget()
        self.__findPathWidget2.getLineEdit().setText(self.__user_image)
        self.__findPathWidget2.added.connect(self.__userImage.setImage)
        self.__findPathWidget3 = FindPathWidget()
        self.__findPathWidget3.getLineEdit().setText(self.__ai_image)
        self.__findPathWidget3.added.connect(self.__AIImage.setImage)

        lay1 = QVBoxLayout()
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.addWidget(self.__homePageGraphicsView)
        lay1.addWidget(self.__findPathWidget1)
        homePageWidget = QWidget()
        homePageWidget.setLayout(lay1)

        lay2 = QHBoxLayout()
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(self.__userImage)
        lay2.addWidget(self.__findPathWidget2)
        userWidget = QWidget()
        userWidget.setLayout(lay2)

        lay3 = QHBoxLayout()
        lay3.setContentsMargins(0, 0, 0, 0)
        lay3.addWidget(self.__AIImage)
        lay3.addWidget(self.__findPathWidget3)
        aiWidget = QWidget()
        aiWidget.setLayout(lay3)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS['Home Image'], homePageWidget)
        lay.addRow(LangClass.TRANSLATIONS['User Image'], userWidget)
        lay.addRow(LangClass.TRANSLATIONS['AI Image'], aiWidget)

        self.__profileWidget = QWidget()
        self.__profileWidget.setLayout(lay)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS['OK'])
        self.__okBtn.clicked.connect(self.__accept)

        cancelBtn = QPushButton(LangClass.TRANSLATIONS['Cancel'])
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__profileWidget)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        # TODO
        self.__rightWidget = ThemeWidget()
        # set the color
        # set the font

        self.__splitter = QSplitter()
        self.__splitter.addWidget(leftWidget)
        self.__splitter.addWidget(self.__rightWidget)
        self.__splitter.setHandleWidth(1)
        self.__splitter.setChildrenCollapsible(False)
        self.__splitter.setSizes([500, 500])
        self.__splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        self.__splitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        lay = QVBoxLayout()
        lay.addWidget(self.__splitter)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)
        self.setLayout(lay)

    def __accept(self):
        self.__settings_ini.setValue('background_image', self.__findPathWidget1.getFileName())
        self.__settings_ini.setValue('user_image', self.__findPathWidget2.getFileName())
        self.__settings_ini.setValue('ai_image', self.__findPathWidget3.getFileName())
        self.__settings_ini.setValue('theme_color', self.__rightWidget.getColor())
        self.__settings_ini.setValue('theme_font', self.__rightWidget.getFont())
        self.accept()