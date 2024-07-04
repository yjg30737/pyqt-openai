from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel
import webbrowser


class LinkLabel(QLabel):
    def __init__(self, text, link):
        super().__init__(text)
        self.link = link
        self.setText(f"<a href=\"{link}\">{text}</a>")
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.linkActivated.connect(lambda: webbrowser.open(link))
        self.setContentsMargins(2, 2, 2, 2)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setOpenExternalLinks(True)
