import os

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QToolButton, QMenu, QAction, QWidget, QHBoxLayout

from pyqt_openai.chat_widget.textEditPropmtGroup import TextEditPropmtGroup
from pyqt_openai.propmt_command_completer.commandSuggestionWidget import CommandSuggestionWidget
from pyqt_openai.res.language_dict import LangClass
from pyqt_openai.sqlite import SqliteDatabase
from pyqt_openai.svgToolButton import SvgToolButton


class Prompt(QWidget):
    onStoppedClicked = Signal()
    onContinuedClicked = Signal()
    onRegenerateClicked = Signal()
    
    def __init__(self, db: SqliteDatabase):
        super().__init__()
        self.__initVal(db)
        self.__initUi()

    def __initVal(self, db):
        self.__db = db

        # prompt group
        self.__p_grp = []

        # False by default
        self.__commandEnabled = False

    def __initUi(self):
        # prompt control buttons
        self.__stopBtn = QPushButton('Stop')
        self.__stopBtn.clicked.connect(self.onStoppedClicked.emit)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.__stopBtn)
        lay.setAlignment(Qt.AlignCenter)

        self.__controlWidgetDuringGeneration = QWidget()
        self.__controlWidgetDuringGeneration.setLayout(lay)

        self.__continueBtn = QPushButton('Continue')
        self.__continueBtn.clicked.connect(self.onContinuedClicked.emit)

        self.__regenerateBtn = QPushButton('Regenerate')
        self.__regenerateBtn.clicked.connect(self.onRegenerateClicked.emit)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.__continueBtn)
        lay.addWidget(self.__regenerateBtn)
        lay.setAlignment(Qt.AlignCenter)

        self.__controlWidgetAfterGeneration = QWidget()
        self.__controlWidgetAfterGeneration.setLayout(lay)

        # Create the command suggestion list
        self.__suggestionWidget = CommandSuggestionWidget()
        self.__suggestion_list = self.__suggestionWidget.getCommandList()

        self.__textEditGroup = TextEditPropmtGroup(self.__db)
        self.__textEditGroup.textChanged.connect(self.updateHeight)

        # set command suggestion
        self.__textEditGroup.onUpdateSuggestion.connect(self.__updateSuggestions)
        self.__textEditGroup.onSendKeySignalToSuggestion.connect(self.__sendKeysignalToSuggestion)

        self.__suggestion_list.itemClicked.connect(self.executeCommand)

        lay = QVBoxLayout()
        lay.addWidget(self.__suggestionWidget)
        lay.addWidget(self.__textEditGroup)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        settingsBtn = SvgToolButton()
        settingsBtn.setIcon('ico/vertical_three_dots.svg')
        settingsBtn.setToolTip(LangClass.TRANSLATIONS['Prompt Settings'])

        # Create the menu
        menu = QMenu(self)

        # Create the actions
        beginningAction = QAction(LangClass.TRANSLATIONS['Show Beginning'], self)
        beginningAction.setShortcut('Ctrl+B')
        beginningAction.setCheckable(True)
        beginningAction.toggled.connect(self.__showBeginning)

        endingAction = QAction(LangClass.TRANSLATIONS['Show Ending'], self)
        endingAction.setShortcut('Ctrl+E')
        endingAction.setCheckable(True)
        endingAction.toggled.connect(self.__showEnding)

        supportPromptCommandAction = QAction(LangClass.TRANSLATIONS['Support Prompt Command'], self)
        supportPromptCommandAction.setShortcut('Ctrl+Shift+P')
        supportPromptCommandAction.setCheckable(True)
        supportPromptCommandAction.toggled.connect(self.__supportPromptCommand)

        readingFilesAction = QAction(LangClass.TRANSLATIONS['Upload Files...'], self)
        readingFilesAction.triggered.connect(self.__readingFiles)

        # Add the actions to the menu
        menu.addAction(beginningAction)
        menu.addAction(endingAction)
        menu.addAction(supportPromptCommandAction)
        menu.addAction(readingFilesAction)

        # Connect the button to the menu
        settingsBtn.setMenu(menu)
        settingsBtn.setPopupMode(QToolButton.InstantPopup)

        lay = QVBoxLayout()
        lay.addWidget(settingsBtn)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setAlignment(Qt.AlignBottom)

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
        lay.addWidget(self.__controlWidgetAfterGeneration)
        lay.addWidget(bottomWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        self.activateDuringGeneratingWidget(False)
        self.activateAfterResponseWidget(False)

        self.__suggestionWidget.setVisible(False)

        self.updateHeight()

    def __getEveryPromptCommands(self):
        # get prop group
        p_grp = []
        for group in self.__db.selectPropPromptGroup():
            p_grp_attr = [attr for attr in self.__db.selectPropPromptAttribute(group[0])]
            p_grp_value = ''
            for attr_obj in p_grp_attr:
                name = attr_obj[2]
                value = attr_obj[3]
                if value and value.strip():
                    p_grp_value += f'{name}: {value}\n'
            p_grp.append({'name': group[1], 'value': p_grp_value})

        # get template group
        t_grp = []
        for group in self.__db.selectTemplatePromptGroup():
            t_grp_attr = [attr for attr in self.__db.selectTemplatePromptUnit(group[0])]
            t_grp_value = ''
            for attr_obj in t_grp_attr:
                name = attr_obj[2]
                value = attr_obj[3]
                t_grp.append({'name': f'{attr_obj[2]}({group[1]})', 'value': value})

        self.__p_grp = p_grp + t_grp

        # TODO will include value as well
        return [command['name'] for command in self.__p_grp]

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

                    # Example: Add some dummy command suggestions
                    commands = self.__getEveryPromptCommands()
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

    def __sendKeysignalToSuggestion(self, key):
        if key == 'up':
            self.__suggestion_list.setCurrentRow(max(0, self.__suggestion_list.currentRow() - 1))
        elif key == 'down':
            self.__suggestion_list.setCurrentRow(
                min(self.__suggestion_list.currentRow() + 1, self.__suggestion_list.count() - 1))
        elif key == 'enter':
            self.executeCommand(self.__suggestion_list.currentItem())

    def activateDuringGeneratingWidget(self, f):
        self.__controlWidgetDuringGeneration.setVisible(f)

    def activateAfterResponseWidget(self, f, continue_f=False):
        self.__controlWidgetAfterGeneration.setVisible(f)
        self.__continueBtn.setVisible(continue_f)

    def executeCommand(self, item):
        self.__textEditGroup.executeCommand(item, self.__p_grp)

    def updateHeight(self):
        overallHeight = self.__textEditGroup.adjustHeight()
        self.setMaximumHeight(overallHeight + self.__suggestionWidget.maximumHeight())

    def getTextEdit(self):
        return self.__textEditGroup.getGroup()[1]

    def getContent(self):
        return self.__textEditGroup.getContent()

    def __showBeginning(self, f):
        self.__textEditGroup.getGroup()[0].setVisible(f)

    def __showEnding(self, f):
        self.__textEditGroup.getGroup()[-1].setVisible(f)

    def __supportPromptCommand(self, f):
        self.__commandEnabled = f
        self.__textEditGroup.setCommandEnabled(f)

    def __readingFiles(self):
        filenames = QFileDialog.getOpenFileNames(self, 'Find', '', 'All Files (*.*)')
        if filenames[0]:
            filenames = filenames[0]
            source_context = ''
            for filename in filenames:
                base_filename = os.path.basename(filename)
                source_context += f'=== {base_filename} start ==='
                source_context += '\n'*2
                with open(filename, 'r', encoding='utf-8') as f:
                    source_context += f.read()
                source_context += '\n'*2
                source_context += f'=== {base_filename} end ==='
                source_context += '\n'*2
            prompt_context = f'== Source Start ==\n{source_context}== Source End =='

            self.__textEditGroup.getGroup()[1].setText(prompt_context)