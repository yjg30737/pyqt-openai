from qtpy.QtWidgets import QWidget, QDialog, QVBoxLayout, QTabWidget
from qtpy.QtGui import QIcon
from qtpy.QtCore import Qt


class GeneralTab(QWidget):
    def __init__(self, parent=None):
        super(GeneralTab, self).__init__(parent)
        self.__initUi()

    def __initUi(self):
        # Language


        # Theme

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


class WindowTab(QWidget):
    def __init__(self, parent=None):
        super(WindowTab, self).__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("ico/setting.svg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(GeneralTab(), "General")
        self.tabs.addTab(WindowTab(), "Window")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())