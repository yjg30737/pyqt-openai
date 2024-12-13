from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtGui import QPixmap

from pyqt_openai import ICON_QUESTION
from pyqt_openai.widgets.svgLabel import SvgLabel

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class QuestionTooltipLabel(SvgLabel):
    def __init__(
        self,
        tooltip: str = "Click for more information",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setPixmap(QPixmap(ICON_QUESTION))
        self.setToolTip(tooltip)
