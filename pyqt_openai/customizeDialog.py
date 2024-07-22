from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QDialog, QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFormLayout, QSplitter, \
    QSizePolicy

from pyqt_openai.constants import IMAGE_FILE_EXT, DEFAULT_ICON_SIZE
from pyqt_openai.fontWidget import FontWidget
from pyqt_openai.models import CustomizeParamsContainer
from pyqt_openai.lang.language_dict import LangClass
from pyqt_openai.widgets.circleProfileImage import RoundedImage
from pyqt_openai.widgets.findPathWidget import FindPathWidget
from pyqt_openai.widgets.normalImageView import NormalImageView


class CustomizeDialog(QDialog):
    def __init__(self, args: CustomizeParamsContainer):
        super().__init__()
        self.__initVal(args)
        self.__initUi()

    def __initVal(self, args):
        self.__background_image = args.background_image
        self.__user_image = args.user_image
        self.__ai_image = args.ai_image
        self.__font_size = args.font_size
        self.__font_family = args.font_family

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS['Customize'])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__homePageGraphicsView = NormalImageView()
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

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        self.__fontWidget = FontWidget(QFont(self.__font_family, self.__font_size))

        self.__splitter = QSplitter()
        self.__splitter.addWidget(leftWidget)
        self.__splitter.addWidget(self.__fontWidget)
        self.__splitter.setHandleWidth(1)
        self.__splitter.setChildrenCollapsible(False)
        self.__splitter.setSizes([500, 500])
        self.__splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        self.__splitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

        self.__okBtn = QPushButton(LangClass.TRANSLATIONS['OK'])
        self.__okBtn.clicked.connect(self.accept)

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
        lay.addWidget(self.__splitter)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

    def getParam(self):
        return CustomizeParamsContainer(
            background_image=self.__findPathWidget1.getFileName(),
            user_image=self.__findPathWidget2.getFileName(),
            ai_image=self.__findPathWidget3.getFileName(),
            font_size=self.__fontWidget.getFont().pointSize(),
            font_family=self.__fontWidget.getFont().family()
        )