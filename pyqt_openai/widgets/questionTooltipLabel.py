from PySide6.QtGui import QPixmap

from pyqt_openai import ICON_QUESTION
from pyqt_openai.widgets.svgLabel import SvgLabel


class QuestionTooltipLabel(SvgLabel):
    def __init__(self, tooltip="Click for more information", parent=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(ICON_QUESTION))
        self.setToolTip(tooltip)