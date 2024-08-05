from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea


class Home(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        title = QLabel('Welcome to Home Page !', self)
        title.setFont(QFont('Arial', 32))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel('Do whatever you can !' + '\n'*2)

        description.setFont(QFont('Arial', 16))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # self.__toLabel = LinkLabel()
        # self.__toLabel.setText('To Replicate / What is Replicate?')
        # self.__toLabel.setUrl('https://replicate.com/')
        # self.__toLabel.setFont(QFont('Arial', 16))
        # self.__toLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #
        # self.__howToUseLabel = LinkLabel()
        # self.__howToUseLabel.setText('How to use Replicate?')
        # self.__howToUseLabel.setUrl('https://replicate.com/account/api-tokens')
        # self.__howToUseLabel.setFont(QFont('Arial', 16))
        # self.__howToUseLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(title)
        lay.addWidget(description)
        # lay.addWidget(self.__toLabel)
        # lay.addWidget(self.__howToUseLabel)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(lay)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setWidget(mainWidget)
        self.setWidgetResizable(True)


    def __setMenuBar(self):
        menubar = self.menuBar()

        # create the "File" menu
        fileMenu = QMenu(LangClass.TRANSLATIONS['File'], self)
        fileMenu.addAction(self.__settingsAction)
        fileMenu.addAction(self.__exitAction)
        menubar.addMenu(fileMenu)

        # create the "Help" menu
        helpMenu = QMenu(LangClass.TRANSLATIONS['Help'], self)
        menubar.addMenu(helpMenu)

        helpMenu.addAction(self.__aboutAction)

        donateMenu = QMenu(LangClass.TRANSLATIONS['Donate'], self)
        donateMenu.addAction(self.__paypalAction)
        donateMenu.addAction(self.__buyMeCoffeeAction)

        menubar.addMenu(donateMenu)