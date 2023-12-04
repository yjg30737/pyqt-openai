import os

from qtpy.QtCore import Qt, Signal, QSettings
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QWidget, QCheckBox, QSplitter, QSpinBox

from pyqt_openai.customizeDialog import FindPathWidget
from pyqt_openai.image_gen_widget.dallEControlWidget import DallEControlWidget
from pyqt_openai.image_gen_widget.imageNavWidget import ImageNavWidget
from pyqt_openai.image_gen_widget.thumbnailView import ThumbnailView
from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.svgButton import SvgButton


class ImageGeneratingToolWidget(QWidget):
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        default_directory = 'image_result'

        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.IniFormat)
        self.__settings_ini.beginGroup('DALLE')

        if not self.__settings_ini.contains('directory'):
            self.__settings_ini.setValue('directory', os.path.join(os.path.expanduser('~'), default_directory))
        if not self.__settings_ini.contains('is_save'):
            self.__settings_ini.setValue('is_save', True)
        if not self.__settings_ini.contains('continue_genearation'):
            self.__settings_ini.setValue('continue_genearation', False)
        if not self.__settings_ini.contains('number_of_images_to_create'):
            self.__settings_ini.setValue('number_of_images_to_create', 2)

        self.__directory = self.__settings_ini.value('directory', type=str)
        self.__is_save = self.__settings_ini.value('is_save', type=bool)
        self.__continue_generation = self.__settings_ini.value('continue_genearation', type=bool)
        self.__number_of_images_to_create = self.__settings_ini.value('number_of_images_to_create', type=int)

        self.__settings_ini.endGroup()

    def __initUi(self):
        self.__imageNavWidget = ImageNavWidget()
        self.__viewWidget = ThumbnailView()
        self.__rightSideBarWidget = DallEControlWidget()

        self.__imageNavWidget.getUrl.connect(self.__viewWidget.setUrl)

        self.__rightSideBarWidget.notifierWidgetActivated.connect(self.notifierWidgetActivated)
        self.__rightSideBarWidget.submitDallE.connect(self.__setResult)

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

        self.__findPathWidget = FindPathWidget()
        self.__findPathWidget.setAsDirectory(True)
        self.__findPathWidget.getLineEdit().setPlaceholderText('Choose Directory to Save...')
        self.__findPathWidget.getLineEdit().setText(self.__directory)
        self.__findPathWidget.added.connect(self.__setSaveDirectory)

        self.__saveChkBox = QCheckBox('Save After Submit')
        self.__saveChkBox.setChecked(self.__is_save)
        self.__saveChkBox.stateChanged.connect(self.__saveChkBoxStateChanged)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__continueGenerationChkBox = QCheckBox('Continue Image Generation')
        self.__continueGenerationChkBox.setChecked(self.__continue_generation)
        self.__continueGenerationChkBox.stateChanged.connect(self.__continueGenerationChkBoxStateChanged)

        self.__numberOfImagesToCreateSpinBox = QSpinBox()
        self.__numberOfImagesToCreateSpinBox.setRange(2, 1000)
        self.__numberOfImagesToCreateSpinBox.setValue(self.__number_of_images_to_create)
        self.__numberOfImagesToCreateSpinBox.valueChanged.connect(self.__numberOfImagesToCreateSpinBoxValueChanged)

        lay = QHBoxLayout()
        lay.addWidget(self.__settingBtn)
        lay.addWidget(self.__historyBtn)
        lay.addWidget(self.__findPathWidget)
        lay.addWidget(self.__saveChkBox)
        lay.addWidget(sep)
        lay.addWidget(self.__continueGenerationChkBox)
        lay.addWidget(self.__numberOfImagesToCreateSpinBox)
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

    def __setResult(self, url):
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = 'Image Generation Complete!')
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)
        arg = self.__rightSideBarWidget.getArgument()
        self.__viewWidget.setUrl(url)
        DB.insertImage(*arg, url)
        self.__imageNavWidget.refresh()

    def __setSaveDirectory(self, directory):
        self.__directory = directory
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('directory', self.__directory)
        self.__settings_ini.endGroup()

    def __saveChkBoxStateChanged(self, state):
        f = state == 2
        self.__is_save = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('is_save', self.__is_save)
        self.__settings_ini.endGroup()

    def __continueGenerationChkBoxStateChanged(self, state):
        f = state == 2
        self.__continue_generation = f
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('continue_generation', self.__continue_generation)
        self.__settings_ini.endGroup()
        self.__numberOfImagesToCreateSpinBox.setEnabled(f)

    def __numberOfImagesToCreateSpinBoxValueChanged(self, value):
        self.__number_of_images_to_create = value
        self.__settings_ini.beginGroup('DALLE')
        self.__settings_ini.setValue('number_of_images_to_create', self.__number_of_images_to_create)
        self.__settings_ini.endGroup()
