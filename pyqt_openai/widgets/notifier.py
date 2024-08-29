import os
import posixpath

from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QSizePolicy

from pyqt_openai import SRC_DIR, ICON_CLOSE, NOTIFIER_MAX_CHAR


class NotifierWidget(QWidget):
    doubleClicked = Signal()

    def __init__(self, informative_text='', detailed_text='', parent=None):
        super().__init__(parent)
        self.__timerVal = 10000
        self.__initUi(informative_text, detailed_text)
        self.__repositionWidget()

    def __initUi(self, informative_text='', detailed_text=''):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)

        self.__informativeTextLabel = QLabel(informative_text) if informative_text else QLabel('Informative')
        self.__detailedTextLabel = QLabel(detailed_text) if detailed_text else QLabel('Detailed')
        self.__detailedTextLabel.setText(self.__detailedTextLabel.text()[:NOTIFIER_MAX_CHAR] + '...')
        self.__detailedTextLabel.setWordWrap(True)

        closeBtn = QPushButton()
        closeBtn.clicked.connect(self.close)
        closeBtn.setIcon(QIcon(ICON_CLOSE))

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)

        self.__btnWidget = QWidget()
        self.__btnWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        lay.addWidget(closeBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        customMenuBar = QWidget()
        customMenuBar.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(customMenuBar)
        lay.addWidget(self.__informativeTextLabel)
        lay.addWidget(self.__detailedTextLabel)
        lay.addWidget(self.__btnWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        lay.setContentsMargins(8, 8, 8, 8)
        self.setLayout(lay)
        self.adjustSize()  # Adjust size after setting the layout

    def __repositionWidget(self):
        ag = QtGui.QGuiApplication.primaryScreen().availableGeometry()

        # Move to bottom right corner
        bottom_right_x = ag.width() - self.width()
        bottom_right_y = ag.height() - self.height()
        self.move(bottom_right_x, bottom_right_y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

        return super().keyPressEvent(event)

    def addWidgets(self, widgets: list):
        for widget in widgets:
            self.__btnWidget.layout().addWidget(widget)
        self.adjustSize()  # Adjust size after adding widgets
        self.__repositionWidget()  # Reposition widget after size adjustment

    def show(self) -> None:
        super().show()
        self.adjustSize()  # Adjust size when showing the widget
        self.__repositionWidget()  # Reposition widget when showing
        QApplication.beep()
        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.__checkTimer)
        self.__timer.start(1000)

    def __checkTimer(self):
        self.__timerVal -= 1000
        if self.__timerVal == 1000:
            self.__showAnimation()
        elif self.__timerVal <= 0:
            self.close()

    def __showAnimation(self):
        self.__animation = QPropertyAnimation(self, b"windowOpacity")
        self.__animation.finished.connect(self.close)
        self.__animation.setDuration(1000)
        self.__animation.setStartValue(1.0)
        self.__animation.setEndValue(0.0)
        self.__animation.start()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        self.close()
        return super().mouseDoubleClickEvent(event)