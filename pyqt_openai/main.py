import openai, os

from chatWidget import Prompt, ChatBrowser

# this API key should be yours
from notifier import NotifierWidget

openai.api_key = '[MY_OPENAPI_API_KEY]'

from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QSplitter, QComboBox, QSpinBox, \
    QFormLayout, QDoubleSpinBox, QPushButton, QFileDialog, QToolBar, QWidgetAction, QHBoxLayout, QAction, QMenu, \
    QSystemTrayIcon, QMessageBox, QSizePolicy, QGroupBox

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

QApplication.setFont(QFont('Arial', 12))


class OpenAIThread(QThread):
    replyGenerated = pyqtSignal(str, bool, bool)

    def __init__(self, openai_arg, idx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__openai_arg = openai_arg
        self.__idx = idx

    def run(self):
        if self.__idx == 0:
            openai_object = openai.Completion.create(
                **self.__openai_arg
            )

            response_text = openai_object['choices'][0]['text'].strip()

            self.replyGenerated.emit(response_text, False, False)
        elif self.__idx == 1:
            try:
                response = openai.Image.create(
                    **self.__openai_arg
                )

                image_url = response['data'][0]['url']

                self.replyGenerated.emit(image_url, False, True)
            except openai.error.InvalidRequestError as e:
                self.replyGenerated.emit('Your request was rejected as a result of our safety system. \n'
                                         'Your prompt may contain text that is not allowed by our safety system.', False)


class OpenAIChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__engine = "text-davinci-003"
        self.__temperature = 0.0
        self.__max_tokens = 256
        self.__top_p = 1.0
        self.__frequency_penalty = 0.0
        self.__presence_penalty = 0.0

    def __initUi(self):
        self.setWindowTitle('PyQt OpenAI Chatbot')
        self.setWindowIcon(QIcon('ico/openai.svg'))
        self.__prompt = Prompt()

        self.__aiTypeCmbBox = QComboBox()
        self.__aiTypeCmbBox.addItems(['Text/Code Completion', 'Image Generation'])

        self.__lineEdit = self.__prompt.getTextEdit()
        self.__lineEdit.setPlaceholderText('Write some text...')
        self.__lineEdit.returnPressed.connect(self.__chat)

        self.__browser = ChatBrowser()

        lay = QHBoxLayout()
        lay.addWidget(self.__aiTypeCmbBox)
        lay.addWidget(self.__prompt)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__aiTypeCmbBox.setMaximumHeight(self.__prompt.sizeHint().height())

        self.__queryWidget = QWidget()
        self.__queryWidget.setLayout(lay)
        self.__queryWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        lay = QVBoxLayout()
        lay.addWidget(self.__browser)
        lay.addWidget(self.__queryWidget)
        lay.setSpacing(0)
        chatWidget = QWidget()
        chatWidget.setLayout(lay)

        # background app
        menu = QMenu()

        action = QAction("Quit", self)
        action.setIcon(QIcon('ico/close.svg'))

        action.triggered.connect(app.quit)

        menu.addAction(action)

        tray_icon = QSystemTrayIcon(app)
        tray_icon.setIcon(QIcon('ico/openai.svg'))
        tray_icon.activated.connect(self.__activated)

        tray_icon.setContextMenu(menu)

        tray_icon.show()

        modelComboBox = QComboBox()
        modelComboBox.addItems([
            'text-davinci-003',
            'text-curie-001',
            'text-babbage-001',
            'text-ada-001',
            'code-davinci-002',
            'code-cushman-001'
        ])
        modelComboBox.setCurrentText(self.__engine)
        modelComboBox.currentTextChanged.connect(self.__modelChanged)

        temperatureSpinBox = QDoubleSpinBox()
        temperatureSpinBox.setRange(0, 1)
        temperatureSpinBox.setAccelerated(True)
        temperatureSpinBox.setSingleStep(0.01)
        temperatureSpinBox.setValue(self.__temperature)
        temperatureSpinBox.valueChanged.connect(self.__temperatureChanged)

        maxTokensSpinBox = QSpinBox()
        maxTokensSpinBox.setRange(0, 4000)
        maxTokensSpinBox.setAccelerated(True)
        maxTokensSpinBox.setValue(self.__max_tokens)
        maxTokensSpinBox.valueChanged.connect(self.__maxTokensChanged)

        toppSpinBox = QDoubleSpinBox()
        toppSpinBox.setRange(0, 1)
        toppSpinBox.setAccelerated(True)
        toppSpinBox.setSingleStep(0.01)
        toppSpinBox.setValue(self.__top_p)
        toppSpinBox.valueChanged.connect(self.__toppChanged)

        frequencyPenaltySpinBox = QDoubleSpinBox()
        frequencyPenaltySpinBox.setRange(0, 2)
        frequencyPenaltySpinBox.setAccelerated(True)
        frequencyPenaltySpinBox.setSingleStep(0.01)
        frequencyPenaltySpinBox.setValue(self.__frequency_penalty)
        frequencyPenaltySpinBox.valueChanged.connect(self.__frequencyPenaltyChanged)

        presencePenaltySpinBox = QDoubleSpinBox()
        presencePenaltySpinBox.setRange(0, 2)
        presencePenaltySpinBox.setAccelerated(True)
        presencePenaltySpinBox.setSingleStep(0.01)
        presencePenaltySpinBox.setValue(self.__presence_penalty)
        presencePenaltySpinBox.valueChanged.connect(self.__presencePenaltyChanged)

        saveAsLogButton = QPushButton('Save')
        saveAsLogButton.clicked.connect(self.__saveAsLog)


        lay = QFormLayout()
        lay.addRow('Model', modelComboBox)
        lay.addRow('Temperature', temperatureSpinBox)
        lay.addRow('Maximum length', maxTokensSpinBox)
        lay.addRow('Top P', toppSpinBox)
        lay.addRow('Frequency penalty', frequencyPenaltySpinBox)
        lay.addRow('Presence penalty', presencePenaltySpinBox)
        lay.addWidget(saveAsLogButton)

        optionGrpBox = QGroupBox()
        optionGrpBox.setTitle('Option')
        optionGrpBox.setLayout(lay)

        fineTuneGrpBox = QGroupBox()
        fineTuneGrpBox.setTitle('Fine-tune training (coming soon)')

        lay = QVBoxLayout()
        lay.addWidget(optionGrpBox)
        lay.addWidget(fineTuneGrpBox)

        self.__sidebarWidget = QWidget()
        self.__sidebarWidget.setLayout(lay)

        mainWidget = QSplitter()
        mainWidget.addWidget(chatWidget)
        mainWidget.addWidget(self.__sidebarWidget)
        mainWidget.setSizes([700, 300])
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

        self.setCentralWidget(mainWidget)
        self.resize(1024, 768)

        self.__browser.showText('Hello!', True)
        self.__browser.showText('Hello! How may i help you?', False)

        self.__lineEdit.setFocus()

        self.__setActions()
        self.__setToolBar()

    def __setActions(self):
        self.__stackAction = QWidgetAction(self)
        self.__stackBtn = QPushButton('Stack on Top')
        self.__stackBtn.setCheckable(True)
        self.__stackBtn.toggled.connect(self.__stackToggle)
        self.__stackAction.setDefaultWidget(self.__stackBtn)

        self.__sideBarAction = QWidgetAction(self)
        self.__sideBarBtn = QPushButton('Show Sidebar')
        self.__sideBarBtn.setCheckable(True)
        self.__sideBarBtn.setChecked(True)
        self.__sideBarBtn.toggled.connect(self.__sidebarWidget.setVisible)
        self.__sideBarAction.setDefaultWidget(self.__sideBarBtn)

        self.__transparentAction = QWidgetAction(self)
        self.__transparentSpinBox = QSpinBox()
        self.__transparentSpinBox.setRange(0, 100)
        self.__transparentSpinBox.setValue(100)
        self.__transparentSpinBox.valueChanged.connect(self.__setTransparency)
        self.__transparentSpinBox.setToolTip('Set Transparency of Window')
        self.__transparentAction.setDefaultWidget(self.__transparentSpinBox)

    def __activated(self, reason):
        if reason == 3:
            self.show()

    def __setToolBar(self):
        toolbar = QToolBar()
        lay = QHBoxLayout()
        toolbar.addAction(self.__stackAction)
        toolbar.addAction(self.__sideBarAction)
        toolbar.addAction(self.__transparentAction)
        toolbar.setLayout(lay)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

    def __chat(self):
        idx = self.__aiTypeCmbBox.currentIndex()
        openai_arg = ''
        if idx == 0:
            openai_arg = {
                'engine': self.__engine,
                'prompt': self.__lineEdit.toPlainText(),
                'temperature': self.__temperature,
                'max_tokens': self.__max_tokens,
                'top_p': self.__top_p,
                'frequency_penalty': self.__frequency_penalty,
                'presence_penalty': self.__presence_penalty,
            }
        elif idx == 1:
            openai_arg = {
                "prompt": self.__lineEdit.toPlainText(),
                "n": 1,
                "size": "1024x1024"
            }
        self.__lineEdit.setEnabled(False)
        self.__t = OpenAIThread(openai_arg, idx)
        self.__t.replyGenerated.connect(self.__browser.showReply)
        self.__browser.showText(self.__lineEdit.toPlainText(), True)
        self.__lineEdit.clear()
        self.__t.start()
        self.__t.finished.connect(self.__afterGenerated)

    def __afterGenerated(self):
        self.__lineEdit.setEnabled(True)
        self.__lineEdit.setFocus()
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget()
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.show)

    def __modelChanged(self, v):
        self.__engine = v

    def __temperatureChanged(self, v):
        self.__temperature = round(v, 2)

    def __maxTokensChanged(self, v):
        self.__max_tokens = round(v, 2)

    def __toppChanged(self, v):
        self.__topp = round(v, 2)

    def __frequencyPenaltyChanged(self, v):
        self.__frequency_penalty = round(v, 2)

    def __presencePenaltyChanged(self, v):
        self.__presence_penalty = round(v, 2)

    def __saveAsLog(self):
        filename = QFileDialog.getSaveFileName(self, 'Save', os.path.expanduser('~'), 'Text File (*.txt)')
        if filename[0]:
            filename = filename[0]
            file_extension = os.path.splitext(filename)[-1]
            if file_extension == '.txt':
                with open(filename, 'w') as f:
                    f.write(self.__browser.getAllText())
                os.startfile(os.path.dirname(filename))

    def __stackToggle(self, f):
        if f:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def __setTransparency(self, v):
        self.setWindowOpacity(v / 100)

    def closeEvent(self, e):
        message = 'The window has been closed. Would you like to continue running this app in the background?'
        closeMessageBox = QMessageBox()
        closeMessageBox.setWindowTitle('Wait!')
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = closeMessageBox.exec()
        # Yes
        if reply == 16384:
            e.accept()
        # No
        elif reply == 65536:
            app.quit()
        return super().closeEvent(e)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = OpenAIChatBot()
    w.show()
    sys.exit(app.exec())