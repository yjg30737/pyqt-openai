import os

from qtpy.QtCore import Qt, QSettings
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QWidget, QSplitter

from pyqt_openai.models import ImagePromptContainer
from pyqt_openai.pyqt_openai_data import DB
from pyqt_openai.replicate_widget.replicateControlWidget import ReplicateControlWidget
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.util.script import get_image_filename_for_saving, open_directory, get_image_prompt_filename_for_saving
from pyqt_openai.widgets.imageNavWidget import ImageNavWidget
from pyqt_openai.widgets.linkLabel import LinkLabel
from pyqt_openai.widgets.notifier import NotifierWidget
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.thumbnailView import ThumbnailView


class ReplicateWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # ini
        self.__settings_ini = QSettings('pyqt_openai.ini', QSettings.Format.IniFormat)

        self.__settings_ini.beginGroup('REPLICATE')

        if not self.__settings_ini.contains('show_history'):
            self.__settings_ini.setValue('show_history', True)
        if not self.__settings_ini.contains('show_setting'):
            self.__settings_ini.setValue('show_setting', True)

        self.__show_history = self.__settings_ini.value('show_history', type=bool)
        self.__show_setting = self.__settings_ini.value('show_setting', type=bool)

        self.__settings_ini.endGroup()

    def __initUi(self):
        self.__imageNavWidget = ImageNavWidget(ImagePromptContainer.get_keys(), 'image_tb')
        self.__viewWidget = ThumbnailView()
        self.__rightSideBarWidget = ReplicateControlWidget()

        self.__imageNavWidget.getContent.connect(self.__viewWidget.setContent)

        self.__rightSideBarWidget.submitReplicate.connect(self.__setResult)
        self.__rightSideBarWidget.submitReplicateAllComplete.connect(self.__imageGenerationAllComplete)

        self.__historyBtn = Button()
        self.__historyBtn.setStyleAndIcon('ico/history.svg')
        self.__historyBtn.setCheckable(True)
        self.__historyBtn.setToolTip('History')
        self.__historyBtn.setChecked(self.__show_history)
        self.__historyBtn.toggled.connect(self.__toggle_history)

        self.__settingBtn = Button()
        self.__settingBtn.setStyleAndIcon('ico/setting.svg')
        self.__settingBtn.setCheckable(True)
        self.__settingBtn.setToolTip('Settings')
        self.__settingBtn.setChecked(self.__show_setting)
        self.__settingBtn.toggled.connect(self.__toggle_setting)

        self.__toReplicateLabel = LinkLabel('To Replicate / What is Replicate?', 'https://replicate.com/')
        self.__howToUseReplicateLabel = LinkLabel('Get Replicate API Token (Need to sign in first)', 'https://replicate.com/account/api-tokens')

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)

        lay = QHBoxLayout()
        lay.addWidget(self.__settingBtn)
        lay.addWidget(self.__historyBtn)
        lay.addWidget(sep1)
        lay.addWidget(self.__toReplicateLabel)
        lay.addWidget(sep2)
        lay.addWidget(self.__howToUseReplicateLabel)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.__menuWidget = QWidget()
        self.__menuWidget.setLayout(lay)
        self.__menuWidget.setMaximumHeight(self.__menuWidget.sizeHint().height())

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)

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

        # Put this below to prevent the widgets pop up when app is opened
        self.__imageNavWidget.setVisible(self.__show_history)
        self.__rightSideBarWidget.setVisible(self.__show_setting)

    def showSecondaryToolBar(self, f):
        self.__menuWidget.setVisible(f)

    def setAIEnabled(self, f):
        self.__rightSideBarWidget.setEnabled(f)

    def __setResult(self, result):
        # save
        if self.__rightSideBarWidget.isSavedEnabled():
            self.__saveResultImage(result)

        self.__viewWidget.setContent(result.data)
        DB.insertImage(result)
        self.__imageNavWidget.refresh()

    def __saveResultImage(self, result):
        directory = self.__rightSideBarWidget.getDirectory()
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, get_image_filename_for_saving(result))
        with open(filename, 'wb') as f:
            f.write(result.data)

        if self.__rightSideBarWidget.getSavePromptAsText():
            txt_filename = get_image_prompt_filename_for_saving(directory, filename)
            with open(txt_filename, 'w') as f:
                f.write(result.prompt)

    def __imageGenerationAllComplete(self):
        if not self.isVisible():
            if self.__settings_ini.value('notify_finish', type=bool):
                self.__notifierWidget = NotifierWidget(informative_text=LangClass.TRANSLATIONS['Response 👌'], detailed_text = 'Image Generation complete.')
                self.__notifierWidget.show()
                self.__notifierWidget.doubleClicked.connect(self.window().show)

                open_directory(self.__rightSideBarWidget.getDirectory())

    def showEvent(self, event):
        self.__imageNavWidget.refresh()
        super().showEvent(event)

    def setColumns(self, columns):
        self.__imageNavWidget.setColumns(columns)

    def __toggle_history(self, f):
        self.__imageNavWidget.setVisible(f)
        self.__show_history = f
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('show_history', f)
        self.__settings_ini.endGroup()

    def __toggle_setting(self, f):
        self.__rightSideBarWidget.setVisible(f)
        self.__show_setting = f
        self.__settings_ini.beginGroup('REPLICATE')
        self.__settings_ini.setValue('show_setting', f)
        self.__settings_ini.endGroup()
