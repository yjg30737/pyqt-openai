import subprocess

from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QDialog, QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, \
    QFileDialog, QFormLayout
from qtpy.QtCore import Qt, Signal

from qtpy.QtWidgets import QLineEdit, QMenu, QAction
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView

from pyqt_openai.circleProfileImage import RoundedImage
from pyqt_openai.res.language_dict import LangClass


class SingleImageGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.__aspectRatioMode = Qt.KeepAspectRatio
        self.__initVal()

    def __initVal(self):
        self._scene = QGraphicsScene()
        self._p = QPixmap()
        self._item = ''

    def setFilename(self, filename: str):
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


class FindPathLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setMouseTracking(True)
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepareMenu)

    def mouseMoveEvent(self, e):
        self.__showToolTip()
        return super().mouseMoveEvent(e)

    def __showToolTip(self):
        text = self.text()
        text_width = self.fontMetrics().boundingRect(text).width()

        if text_width > self.width():
            self.setToolTip(text)
        else:
            self.setToolTip('')

    def __prepareMenu(self, pos):
        menu = QMenu(self)
        openDirAction = QAction(LangClass.TRANSLATIONS['Open Path'])
        openDirAction.setEnabled(self.text().strip() != '')
        openDirAction.triggered.connect(self.__openPath)
        menu.addAction(openDirAction)
        menu.exec(self.mapToGlobal(pos))

    def __openPath(self):
        filename = self.text()
        path = filename.replace('/', '\\')
        subprocess.Popen(r'explorer /select,"' + path + '"')


class FindPathWidget(QWidget):
    findClicked = Signal()
    added = Signal(str)

    def __init__(self, default_filename: str = ''):
        super().__init__()
        self.__initVal()
        self.__initUi(default_filename)

    def __initVal(self):
        self.__ext_of_files = ''
        self.__directory = False

    def __initUi(self, default_filename: str = ''):
        self.__pathLineEdit = FindPathLineEdit()
        if default_filename:
            self.__pathLineEdit.setText(default_filename)

        self.__pathFindBtn = QPushButton(LangClass.TRANSLATIONS['Find...'])

        self.__pathFindBtn.clicked.connect(self.__find)

        self.__pathLineEdit.setMaximumHeight(self.__pathFindBtn.sizeHint().height())

        lay = QHBoxLayout()
        lay.addWidget(self.__pathLineEdit)
        lay.addWidget(self.__pathFindBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def setLabel(self, text):
        self.layout().insertWidget(0, QLabel(text))

    def setExtOfFiles(self, ext_of_files):
        self.__ext_of_files = ext_of_files

    def getLineEdit(self):
        return self.__pathLineEdit

    def getButton(self):
        return self.__pathFindBtn

    def getFileName(self):
        return self.__pathLineEdit.text()

    def setCustomFind(self, f: bool):
        if f:
            self.__pathFindBtn.clicked.disconnect(self.__find)
            self.__pathFindBtn.clicked.connect(self.__customFind)

    def __customFind(self):
        self.findClicked.emit()

    def __find(self):
        if self.isForDirectory():
            filename = QFileDialog.getExistingDirectory(self, 'Open Directory', '', QFileDialog.ShowDirsOnly)
            if filename:
                pass
            else:
                return
        else:
            str_exp_files_to_open = self.__ext_of_files if self.__ext_of_files else 'All Files (*.*)'
            filename = QFileDialog.getOpenFileName(self, 'Find', '', str_exp_files_to_open)
            if filename[0]:
                filename = filename[0]
            else:
                return
        self.__pathLineEdit.setText(filename)
        self.added.emit(filename)

    def setAsDirectory(self, f: bool):
        self.__directory = f

    def isForDirectory(self) -> bool:
        return self.__directory


class CustomizeDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        pass

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['Customize (working)'])
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        homePageGraphicsView = SingleImageGraphicsView()

        userImage = RoundedImage()
        userImage.setMaximumSize(24, 24)
        userImage.setImage('ico/user.svg')
        AIImage = RoundedImage()
        AIImage.setImage('ico/openai.svg')
        AIImage.setMaximumSize(24, 24)

        findPathWidget1 = FindPathWidget()
        findPathWidget1.added.connect(homePageGraphicsView.setFilename)
        findPathWidget2 = FindPathWidget()
        findPathWidget2.added.connect(userImage.setImage)
        findPathWidget3 = FindPathWidget()
        findPathWidget3.added.connect(AIImage.setImage)

        lay1 = QVBoxLayout()
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.addWidget(homePageGraphicsView)
        lay1.addWidget(findPathWidget1)
        homePageWidget = QWidget()
        homePageWidget.setLayout(lay1)

        lay2 = QHBoxLayout()
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(userImage)
        lay2.addWidget(findPathWidget2)
        userWidget = QWidget()
        userWidget.setLayout(lay2)

        lay3 = QHBoxLayout()
        lay3.setContentsMargins(0, 0, 0, 0)
        lay3.addWidget(AIImage)
        lay3.addWidget(findPathWidget3)
        aiWidget = QWidget()
        aiWidget.setLayout(lay3)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS['Home Image'], homePageWidget)
        lay.addRow(LangClass.TRANSLATIONS['User Image'], userWidget)
        lay.addRow(LangClass.TRANSLATIONS['AI Image'], aiWidget)

        self.__topWidget = QWidget()
        self.__topWidget.setLayout(lay)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS['OK'])
        self.__okBtn.clicked.connect(self.accept)

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
        lay.addWidget(self.__topWidget)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)