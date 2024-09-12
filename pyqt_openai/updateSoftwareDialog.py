import subprocess
import sys

import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QDialogButtonBox

from pyqt_openai import __version__, OWNER, PACKAGE_NAME, UPDATE_DIR, CURRENT_FILENAME, UPDATER_PATH, is_frozen


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

        update_url = f"https://github.com/{self.__owner}/{self.__repo}/releases/download/{self.__recent_version}/VividNode.zip"

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(lambda: run_updater(update_url))
        buttonBox.rejected.connect(self.reject)

        askLbl = QLabel("Do you want to update?")

        lay.addWidget(self.releaseNoteBrowser)
        lay.addWidget(askLbl)
        lay.addWidget(buttonBox)


def check_for_updates(current_version, owner, repo):
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"

        response = requests.get(url)
        releases = response.json()

        update_available = False
        release_notes_html = "<ul>"
        recent_version = current_version
        for release in releases:
            release_version = release['tag_name'].lstrip('v')
            if release_version > current_version:
                recent_version = release_version if recent_version < release_version else recent_version
                update_available = True
                release_notes_html += f'<li><a href="{release["html_url"]}" target="_blank">{release["tag_name"]}</a></li>'
        release_notes_html += "</ul>"

        if update_available:
            return {'release_notes': release_notes_html, 'recent_version': recent_version}
        else:
            return None

    except Exception as e:
        return f"<p>Error fetching release notes: {str(e)}</p>"


def check_for_updates_and_show_dialog(current_version, owner, repo):
    result_dict = check_for_updates(current_version, owner, repo)
    if result_dict:
        release_notes = result_dict['release_notes']
        recent_version = result_dict['recent_version']
        if release_notes:
            # If updates are available, show the update dialog
            update_dialog = UpdateSoftwareDialog(owner, repo, recent_version)
            update_dialog.releaseNoteBrowser.setHtml(release_notes)
            update_dialog.exec()


def update_software():
    # Replace with actual values
    current_version = __version__
    owner = OWNER
    repo = PACKAGE_NAME

    if not is_frozen():
        return

    # Check for updates and show dialog if available
    check_for_updates_and_show_dialog(current_version, owner, repo)


def run_updater(update_url):
    subprocess.Popen([UPDATER_PATH, update_url, UPDATE_DIR, CURRENT_FILENAME], shell=True)
    sys.exit(0)
