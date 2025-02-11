from __future__ import annotations

import datetime

from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

import pyqt_openai

from pyqt_openai import CONTACT, DEFAULT_APP_ICON, DEFAULT_APP_NAME, LICENSE_URL
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.linkLabel import LinkLabel


class AboutDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle(LangClass.TRANSLATIONS["About"])
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.__okBtn: QPushButton = QPushButton(LangClass.TRANSLATIONS["OK"])
        self.__okBtn.clicked.connect(self.accept)

        p = QPixmap(DEFAULT_APP_ICON)
        logoLbl = QLabel()
        logoLbl.setPixmap(p)

        descWidget1 = QLabel()
        descWidget1.setText(
            f"""
        <h1>{DEFAULT_APP_NAME}</h1>
        Software Version {pyqt_openai.__version__}<br/><br/>
        © 2023 {datetime.datetime.now().year}. Used under the {pyqt_openai.LICENSE} License.<br/>
        Copyright (c) {datetime.datetime.now().year} {pyqt_openai.__author__}<br/>
        """,
        )

        descWidget2 = LinkLabel()
        descWidget2.setText(LangClass.TRANSLATIONS["Read MIT License Full Text"])
        descWidget2.setUrl(LICENSE_URL)

        descWidget3 = QLabel()
        descWidget3.setText(
            f"""
        <br/><br/>Contact: {CONTACT}<br/>
        <p><br><br> qtpy, GPT4Free, LiteLLM,<br>LlamaIndex</p>
        """,
        )

        descWidget1.setAlignment(Qt.AlignmentFlag.AlignTop)
        descWidget2.setAlignment(Qt.AlignmentFlag.AlignTop)
        descWidget3.setAlignment(Qt.AlignmentFlag.AlignTop)

        lay = QVBoxLayout()
        lay.addWidget(descWidget1)
        lay.addWidget(descWidget2)
        lay.addWidget(descWidget3)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.setContentsMargins(0, 0, 0, 0)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(logoLbl)
        lay.addWidget(rightWidget)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        cancelBtn = QPushButton(LangClass.TRANSLATIONS["Cancel"])
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)
