import base64

import requests
import os

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter

from pyqt_openai.image_gen_widget.dallEControlWidget import DallEControlWidget
from pyqt_openai.image_gen_widget.imageNavWidget import ImageNavWidget
from pyqt_openai.image_gen_widget.thumbnailView import ThumbnailView
from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.svgButton import SvgButton
from pyqt_openai.util.script import get_image_filename_for_saving, open_directory


class ImageGeneratingToolWidget(QWidget):
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__imageNavWidget = ImageNavWidget()
        self.__viewWidget = ThumbnailView()
        self.__rightSideBarWidget = DallEControlWidget()

        self.__imageNavWidget.getContent.connect(self.__viewWidget.setContent)

        self.__rightSideBarWidget.notifierWidgetActivated.connect(self.notifierWidgetActivated)
        self.__rightSideBarWidget.submitDallE.connect(self.__setResult)
        self.__rightSideBarWidget.submitDallEAllComplete.connect(self.__imageGenerationAllComplete)

        self.__historyBtn = SvgButton()
        self.__historyBtn.setIcon('ico/history.svg')
        self.__historyBtn.setCheckable(True)
        self.__historyBtn.setToolTip('History')
        self.__historyBtn.setChecked(True)
        self.__historyBtn.toggled.connect(self.__imageNavWidget.setVisible)

        self.__settingBtn = SvgButton()
        self.__settingBtn.setIcon('ico/setting.svg')
        self.__settingBtn.setCheckable(True)
        self.__settingBtn.setToolTip('Settings')
        self.__settingBtn.setChecked(True)
        self.__settingBtn.toggled.connect(self.__rightSideBarWidget.setVisible)

        lay = QHBoxLayout()
        lay.addWidget(self.__settingBtn)
        lay.addWidget(self.__historyBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__imageNavWidget)
        mainWidget.addWidget(self.__viewWidget)
        mainWidget.addWidget(self.__rightSideBarWidget)
        mainWidget.setSizes([200, 500, 300])
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setHandleWidth(2)
        mainWidget.setStyleSheet(
        '''
        QSplitter::handle:horizontal
        {
            background: #CCC;
            height: 1px;
        }
        ''')

        lay = QVBoxLayout()
        lay.addWidget(self.__menuWidget)
        lay.addWidget(sep)
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setLayout(lay)

    def showAiToolBar(self, f):
        self.__menuWidget.setVisible(f)

    def setAIEnabled(self, f):
        self.__rightSideBarWidget.setEnabled(f)

    def __setResult(self, image_data):
        arg = self.__rightSideBarWidget.getArgument()

        # save
        if self.__rightSideBarWidget.isSavedEnabled():
            self.__saveResultImage(arg, image_data)

        self.__viewWidget.setContent(image_data)
        DB.insertImage(*arg, image_data)
        self.__imageNavWidget.refresh()

    def __saveResultImage(self, arg, content):
        directory = self.__rightSideBarWidget.getDirectory()
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, get_image_filename_for_saving(arg))
        with open(filename, 'wb') as f:
            f.write(content)

    def __imageGenerationAllComplete(self):
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = 'Image Generation complete.')
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)

        open_directory(self.__rightSideBarWidget.getDirectory())
