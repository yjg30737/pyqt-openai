from qtpy.QtGui import QPixmap

from pyqt_openai import ICON_QUESTION
from pyqt_openai.widgets.svgLabel import SvgLabel


class QuestionTooltipLabel(SvgLabel):
    def __init__(self, parent=None, tooltip="Click for more information"):
        super().__init__()
        self.setPixmap(QPixmap(ICON_QUESTION))
        self.setToolTip(tooltip)