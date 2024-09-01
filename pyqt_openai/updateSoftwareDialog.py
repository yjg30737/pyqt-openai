import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QTextBrowser, QDialogButtonBox

from pyqt_openai import __version__


class UpdateSoftwareDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # TODO LANGUAGE
        self.setWindowTitle("Update Software")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        lay = QVBoxLayout()

        self.setLayout(lay)

        self.__lbl = QLabel("A new version of the software is available.")
        lay.addWidget(self.__lbl)

        self.releaseNoteBrowser = QTextBrowser()
        self.releaseNoteBrowser.setOpenExternalLinks(True)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.updateSoftware)
        buttonBox.rejected.connect(self.reject)

        askLbl = QLabel("Do you want to update?")

        lay.addWidget(self.releaseNoteBrowser)
        lay.addWidget(askLbl)
        lay.addWidget(buttonBox)

    def updateSoftware(self):
        print("Starting software update...")
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UpdateSoftwareDialog(__version__)
    w.show()
    sys.exit(app.exec())
