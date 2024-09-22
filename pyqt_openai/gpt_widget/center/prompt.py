from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QToolButton, QMenu, QWidget, QHBoxLayout, \
    QMessageBox

from pyqt_openai import READ_FILE_EXT_LIST_STR, PROMPT_BEGINNING_KEY_NAME, \
    PROMPT_END_KEY_NAME, PROMPT_JSON_KEY_NAME, DEFAULT_SHORTCUT_PROMPT_BEGINNING, DEFAULT_SHORTCUT_PROMPT_ENDING, \
    DEFAULT_SHORTCUT_SUPPORT_PROMPT_COMMAND, ICON_VERTICAL_THREE_DOTS, ICON_SEND, PROMPT_MAIN_KEY_NAME, \
    IMAGE_FILE_EXT_LIST, \
    TEXT_FILE_EXT_LIST, QFILEDIALOG_DEFAULT_DIRECTORY, DEFAULT_SHORTCUT_SEND, DEFAULT_SHORTCUT_RECORD, ICON_RECORD
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.globals import DB, STTThread, RecorderThread
from pyqt_openai.gpt_widget.center.commandSuggestionWidget import CommandSuggestionWidget
from pyqt_openai.gpt_widget.center.textEditPromptGroup import TextEditPromptGroup
from pyqt_openai.gpt_widget.center.uploadedImageFileWidget import UploadedImageFileWidget
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.util.script import get_content_of_text_file_for_send
from pyqt_openai.widgets.button import Button
from pyqt_openai.widgets.toolButton import ToolButton


class Prompt(QWidget):
    onRecording = Signal(bool)
    onStoppedClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        # prompt group
        self.__p_grp = []

        # False by default
        self.__commandEnabled = False

        self.__json_object = CONFIG_MANAGER.get_general_property('json_object')

        self.stt_thread = None

    def __initUi(self):
        # Prompt control buttons
        self.__stopBtn = QPushButton(LangClass.TRANSLATIONS['Stop'])
        self.__stopBtn.clicked.connect(self.onStoppedClicked.emit)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.__stopBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__controlWidgetDuringGeneration = QWidget()
        self.__controlWidgetDuringGeneration.setLayout(lay)

        # Create the command suggestion list
        self.__suggestionWidget = CommandSuggestionWidget()
        self.__suggestion_list = self.__suggestionWidget.getCommandList()

        self.__uploadedImageFileWidget = UploadedImageFileWidget()

        self.__textEditGroup = TextEditPromptGroup()
        self.__textEditGroup.textChanged.connect(self.updateHeight)

        # set command suggestion
        self.__textEditGroup.onUpdateSuggestion.connect(self.__updateSuggestions)
        self.__textEditGroup.onSendKeySignalToSuggestion.connect(self.__sendKeySignalToSuggestion)
        self.__textEditGroup.onPasteFile.connect(self.__uploadedImageFileWidget.addImageBuffer)

        self.__suggestion_list.itemClicked.connect(self.executeCommand)

        lay = QVBoxLayout()
        lay.addWidget(self.__suggestionWidget)
        lay.addWidget(self.__uploadedImageFileWidget)
        lay.addWidget(self.__textEditGroup)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        self.__sendBtn = Button()
        self.__sendBtn.setStyleAndIcon(ICON_SEND)
        self.__sendBtn.setToolTip(LangClass.TRANSLATIONS['Send'] + f' ({DEFAULT_SHORTCUT_SEND})')
        self.__sendBtn.setShortcut(DEFAULT_SHORTCUT_SEND)

        self.__recordBtn = Button()
        self.__recordBtn.setStyleAndIcon(ICON_RECORD)
        self.__recordBtn.setToolTip(LangClass.TRANSLATIONS['Record'])
        self.__recordBtn.setCheckable(True)
        self.__recordBtn.setShortcut(DEFAULT_SHORTCUT_RECORD)

        settingsBtn = ToolButton()
        settingsBtn.setStyleAndIcon(ICON_VERTICAL_THREE_DOTS)
        settingsBtn.setToolTip(LangClass.TRANSLATIONS['Prompt Settings'])

        # Create the menu
        menu = QMenu(self)

        # Create the actions
        beginningAction = QAction(LangClass.TRANSLATIONS['Show Beginning'] + f' ({DEFAULT_SHORTCUT_PROMPT_BEGINNING})', self)
        beginningAction.setShortcut(DEFAULT_SHORTCUT_PROMPT_BEGINNING)
        beginningAction.setCheckable(True)
        beginningAction.toggled.connect(self.__showBeginning)

        endingAction = QAction(LangClass.TRANSLATIONS['Show Ending'] + f' ({DEFAULT_SHORTCUT_PROMPT_ENDING})', self)
        endingAction.setShortcut(DEFAULT_SHORTCUT_PROMPT_ENDING)
        endingAction.setCheckable(True)
        endingAction.toggled.connect(self.__showEnding)

        supportPromptCommandAction = QAction(LangClass.TRANSLATIONS['Support Prompt Command'] + f' ({DEFAULT_SHORTCUT_SUPPORT_PROMPT_COMMAND})', self)
        supportPromptCommandAction.setShortcut(DEFAULT_SHORTCUT_SUPPORT_PROMPT_COMMAND)
        supportPromptCommandAction.setCheckable(True)
        supportPromptCommandAction.toggled.connect(self.__supportPromptCommand)

        readingFilesAction = QAction(LangClass.TRANSLATIONS['Upload Files...'], self)
        readingFilesAction.triggered.connect(self.__readingFiles)

        self.__writeJSONAction = QAction(LangClass.TRANSLATIONS['Write JSON'], self)
        self.__writeJSONAction.toggled.connect(self.__showJSON)
        self.__writeJSONAction.setCheckable(True)
        self.__toggleJSONAction(self.__json_object)

        # Add the actions to the menu
        menu.addAction(beginningAction)
        menu.addAction(endingAction)
        menu.addAction(supportPromptCommandAction)
        menu.addAction(self.__writeJSONAction)
        menu.addAction(readingFilesAction)

        # Connect the button to the menu
        settingsBtn.setMenu(menu)
        settingsBtn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        lay = QHBoxLayout()
        lay.addWidget(self.__recordBtn)
        lay.addWidget(self.__sendBtn)
        lay.addWidget(settingsBtn)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setSpacing(0)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(leftWidget)
        lay.addWidget(rightWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__controlWidgetDuringGeneration)
        lay.addWidget(bottomWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.showWidgetInPromptDuringResponse(False)

        self.__suggestionWidget.setVisible(False)

        self.updateHeight()

        self.__sendBtn.clicked.connect(self.getMainPromptInput().sendMessage)

        self.__recordBtn.toggled.connect(self.record)

        self.__textEditGroup.installEventFilter(self)

    def __setEveryPromptCommands(self):
        command_obj_lst = []
        for group in DB.selectPromptGroup():
            entries = [attr for attr in DB.selectPromptEntry(group_id=group.id)]
            if group.prompt_type == 'form':
                value = ''
                for entry in entries:
                    content = entry.content
                    if content and content.strip():
                        value += f'{entry.name}: {content}\n'
                command_obj_lst.append({
                    'name': group.name,
                    'value': value
                })
            elif group.prompt_type == 'sentence':
                for entry in entries:
                    command_obj_lst.append({
                        'name': f'{entry.name}({group.name})',
                        'value': entry.content
                    })
        self.__p_grp = [{'name': obj['name'], 'value': obj['value']} for obj in command_obj_lst]

    def __getEveryPromptCommands(self, get_name_only=False):
        if get_name_only:
            return [obj['name'] for obj in self.__p_grp]
        return self.__p_grp

    def __updateSuggestions(self):
        w = self.__textEditGroup.getCurrentTextEdit()
        if w and self.__commandEnabled:
            input_text_chunk = w.toPlainText().split()
            input_text_chunk_exists = len(input_text_chunk) > 0
            self.__suggestionWidget.setVisible(input_text_chunk_exists)
            if input_text_chunk_exists:
                input_text_chunk = input_text_chunk[-1]
                starts_with_f = input_text_chunk.startswith('/')
                self.__suggestionWidget.setVisible(starts_with_f)
                w.setCommandSuggestionEnabled(starts_with_f)
                if starts_with_f:
                    command_word = input_text_chunk[1:]
                    # Set every prompt commands first
                    self.__setEveryPromptCommands()
                    # Get the commands
                    commands = self.__getEveryPromptCommands(get_name_only=True)
                    filtered_commands = commands
                    if command_word:
                        filtered_commands = [command for command in commands if command_word.lower() in command.lower()]
                    filtered_commands_exists_f = len(filtered_commands) > 0
                    self.__suggestionWidget.setVisible(filtered_commands_exists_f)
                    if filtered_commands_exists_f:
                        # Clear previous suggestions
                        self.__suggestion_list.clear()

                        # Add the filtered suggestions to the list
                        self.__suggestion_list.addItems(filtered_commands)
                        self.__suggestion_list.setCurrentRow(0)

    def __sendKeySignalToSuggestion(self, key):
        if key == 'up':
            self.__suggestion_list.setCurrentRow(max(0, self.__suggestion_list.currentRow() - 1))
        elif key == 'down':
            self.__suggestion_list.setCurrentRow(
                min(self.__suggestion_list.currentRow() + 1, self.__suggestion_list.count() - 1))
        elif key == 'enter':
            self.executeCommand(self.__suggestion_list.currentItem())

    def showWidgetInPromptDuringResponse(self, f):
        self.__controlWidgetDuringGeneration.setVisible(f)

    def executeCommand(self, item):
        self.__textEditGroup.executeCommand(item, self.__p_grp)

    def updateHeight(self):
        overallHeight = self.__textEditGroup.adjustHeight()
        # Set the maximum height of the widget - should fit the device screen
        self.setMaximumHeight(overallHeight + self.__suggestionWidget.height() + self.__uploadedImageFileWidget.height() + 100)

    def getMainPromptInput(self):
        return self.__textEditGroup.getMainTextEdit()

    def getContent(self):
        return self.__textEditGroup.getContent()

    def getJSONContent(self):
        return self.__textEditGroup.getJSONContent()

    def __showBeginning(self, f):
        self.__textEditGroup.setVisibleTo(PROMPT_BEGINNING_KEY_NAME, f)
        if f:
            self.__textEditGroup.getGroup()[PROMPT_BEGINNING_KEY_NAME].setFocus()
        else:
            self.__textEditGroup.getGroup()[PROMPT_BEGINNING_KEY_NAME].clear()
            self.__textEditGroup.getGroup()[PROMPT_MAIN_KEY_NAME].setFocus()

    def __showEnding(self, f):
        self.__textEditGroup.setVisibleTo(PROMPT_END_KEY_NAME, f)
        if f:
            self.__textEditGroup.getGroup()[PROMPT_END_KEY_NAME].setFocus()
        else:
            self.__textEditGroup.getGroup()[PROMPT_END_KEY_NAME].clear()
            self.__textEditGroup.getGroup()[PROMPT_MAIN_KEY_NAME].setFocus()

    def __supportPromptCommand(self, f):
        self.__commandEnabled = f
        self.__textEditGroup.setCommandEnabled(f)

    def __readingFiles(self):
        filenames = QFileDialog.getOpenFileNames(self, LangClass.TRANSLATIONS['Find'], QFILEDIALOG_DEFAULT_DIRECTORY, READ_FILE_EXT_LIST_STR)
        if filenames[0]:
            filenames = filenames[0]
            cur_file_extension = Path(filenames[0]).suffix
            # Text
            if cur_file_extension in TEXT_FILE_EXT_LIST:
                prompt_context = get_content_of_text_file_for_send(filenames)
                self.getMainPromptInput().setText(prompt_context)
            # Image
            elif cur_file_extension in IMAGE_FILE_EXT_LIST:
                self.__uploadedImageFileWidget.addFiles(filenames)

    def getImageBuffers(self):
        return self.__uploadedImageFileWidget.getImageBuffers()

    def resetUploadImageFileWidget(self):
        self.__uploadedImageFileWidget.setVisible(False)
        self.__uploadedImageFileWidget.clear()

    def __toggleJSONAction(self, f):
        self.__writeJSONAction.setEnabled(f)
        self.__writeJSONAction.setChecked(f)

    def toggleJSON(self, f):
        self.__toggleJSONAction(f)
        self.__showJSON(f)
        json_text_edit = self.__textEditGroup.getGroup()[PROMPT_JSON_KEY_NAME]
        json_text_edit.clear()
        if f:
            json_text_edit.setFocus()
        else:
            self.__textEditGroup.getGroup()[PROMPT_MAIN_KEY_NAME].setFocus()

    def __showJSON(self, f):
        self.__json_object = f
        self.__textEditGroup.setVisibleTo(PROMPT_JSON_KEY_NAME, f)

    def sendEnabled(self, f):
        self.getMainPromptInput().setEnabled(f)
        self.__sendBtn.setEnabled(f)

    def eventFilter(self, source, event):
        if event.type() == 6:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.__sendBtn.click()
                    return True
        return super().eventFilter(source, event)

    def record(self, checked):
        if checked:
            self.recorder_thread = RecorderThread()
            self.recorder_thread.recording_finished.connect(self.on_recording_finished)
            if self.__textEditGroup.getCurrentTextEdit():
                self.__textEditGroup.getCurrentTextEdit().clear()
            self.recorder_thread.start()
        else:
            self.recorder_thread.stop()

    def on_recording_finished(self, filename):
        self.__recordBtn.setChecked(False)
        self.stt_thread = STTThread(filename)
        self.stt_thread.stt_finished.connect(self.on_stt_finished)
        self.stt_thread.errorGenerated.connect(
            lambda x: QMessageBox.critical(self, LangClass.TRANSLATIONS['Error'], x)
        )
        self.stt_thread.start()

    def on_stt_finished(self, text):
        t = self.__textEditGroup.getCurrentTextEdit()
        if t:
            t.setText(text)
        else:
            self.__textEditGroup.getMainTextEdit().setText(text)