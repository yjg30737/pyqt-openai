from __future__ import annotations

from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QDialog, QLabel, QVBoxLayout

from pyqt_openai import IMAGE_IMPORT_PROMPT_WITH_CSV_RIGHT_FORM
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.normalImageView import NormalImageView


class PromptCSVRightFormSampleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["CSV Right Form Sample"])
        # Add image
        view = NormalImageView()
        view.setFilename(IMAGE_IMPORT_PROMPT_WITH_CSV_RIGHT_FORM)
        # Anti-aliasing
        view.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        lay = QVBoxLayout()
        lay.addWidget(view)
        lay.addWidget(QLabel("This is from awesome_chatgpt_prompt.csv file from huggingface."))

        self.setLayout(lay)
