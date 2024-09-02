import sys, requests, zipfile

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QTextBrowser, QDialogButtonBox

from pyqt_openai import __version__
from pyqt_openai.util.script import update_software


class UpdateSoftwareDialog(QDialog):
    def __init__(self, owner, repo, recent_version, parent=None):
        super().__init__(parent)
        self.__initVal(owner, repo, recent_version)
        self.__initUi()

    def __initVal(self, owner, repo, recent_version):
        self.__owner = owner
        self.__repo = repo
        self.__recent_version = f'v{recent_version}'

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
        buttonBox.accepted.connect(lambda: update_software())
        buttonBox.rejected.connect(self.reject)

        askLbl = QLabel("Do you want to update?")

        lay.addWidget(self.releaseNoteBrowser)
        lay.addWidget(askLbl)
        lay.addWidget(buttonBox)



