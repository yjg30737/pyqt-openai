from qtpy.QtCore import Qt, QSettings
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QDialog, QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFormLayout
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView

from pyqt_openai.constants import IMAGE_FILE_EXT, DEFAULT_ICON_SIZE
from pyqt_openai.widgets.circleProfileImage import RoundedImage
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.res.language_dict import LangClass


class SingleImageGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.__aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio
        self.__initVal()

    def __initVal(self):
        self._scene = QGraphicsScene()
        self._p = QPixmap()
        self._item = ''

    def setFilename(self, filename: str):
        if filename == '':
            pass
        else:
            self._p = QPixmap(filename)
            self._setPixmap(self._p)

    def setPixmap(self, p):
        self._setPixmap(p)

    def _setPixmap(self, p):
        self._p = p
        self._scene = QGraphicsScene()
        self._item = self._scene.addPixmap(self._p)
        self.setScene(self._scene)
        self.fitInView(self._item, self.__aspectRatioMode)

    def setAspectRatioMode(self, mode):
        self.__aspectRatioMode = mode

    def resizeEvent(self, e):
        if self._item:
            self.fitInView(self._item, self.__aspectRatioMode)
        return super().resizeEvent(e)



class CustomizeDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)

        if not self.__settings_ini.contains('background_image'):
            self.__settings_ini.setValue('background_image', '')
        if not self.__settings_ini.contains('user_image'):
            self.__settings_ini.setValue('user_image', 'ico/user.png')
        if not self.__settings_ini.contains('ai_image'):
            self.__settings_ini.setValue('ai_image', 'ico/openai.png')

        self.__background_image = self.__settings_ini.value('background_image', type=str)
        self.__user_image = self.__settings_ini.value('user_image', type=str)
        self.__ai_image = self.__settings_ini.value('ai_image', type=str)

    def __initUi(self):
        self.setWindowTitle('Customize')
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__homePageGraphicsView = SingleImageGraphicsView()
        self.__homePageGraphicsView.setFilename(self.__background_image)

        self.__userImage = RoundedImage()
        self.__userImage.setMaximumSize(*DEFAULT_ICON_SIZE)
        self.__userImage.setImage(self.__user_image)
        self.__AIImage = RoundedImage()
        self.__AIImage.setImage(self.__ai_image)
        self.__AIImage.setMaximumSize(*DEFAULT_ICON_SIZE)

        self.__findPathWidget1 = FindPathWidget()
        self.__findPathWidget1.getLineEdit().setText(self.__background_image)
        self.__findPathWidget1.added.connect(self.__homePageGraphicsView.setFilename)
        self.__findPathWidget1.setExtOfFiles(IMAGE_FILE_EXT)

        self.__findPathWidget2 = FindPathWidget()
        self.__findPathWidget2.getLineEdit().setText(self.__user_image)
        self.__findPathWidget2.added.connect(self.__userImage.setImage)
        self.__findPathWidget2.setExtOfFiles(IMAGE_FILE_EXT)

        self.__findPathWidget3 = FindPathWidget()
        self.__findPathWidget3.getLineEdit().setText(self.__ai_image)
        self.__findPathWidget3.added.connect(self.__AIImage.setImage)
        self.__findPathWidget3.setExtOfFiles(IMAGE_FILE_EXT)

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

        self.__topWidget = QWidget()
        self.__topWidget.setLayout(lay)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS['OK'])
        self.__okBtn.clicked.connect(self.__accept)

        cancelBtn = QPushButton(LangClass.TRANSLATIONS['Cancel'])
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__topWidget)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

    def __accept(self):
        self.__settings_ini.setValue('background_image', self.__findPathWidget1.getFileName())
        self.__settings_ini.setValue('user_image', self.__findPathWidget2.getFileName())
        self.__settings_ini.setValue('ai_image', self.__findPathWidget3.getFileName())
        self.accept()