from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QAbstractAnimation, QPoint
from PySide6.QtGui import QFont, QColor

from pyqt_openai import (
    TOAST_DURATION,
    DEFAULT_TOAST_BACKGROUND_COLOR,
    DEFAULT_TOAST_FOREGROUND_COLOR,
)


class Toast(QWidget):
    def __init__(self, text, duration=TOAST_DURATION, parent=None):
        super().__init__(parent)
        self.__initVal(parent, duration)
        self.__initUi(text)

    def __initVal(self, parent, duration):
        self.__parent = parent
        self.__parent.installEventFilter(self)
        self.installEventFilter(self)
        self.__timer = QTimer(self)
        self.__duration = duration
        self.__opacity = 0.8
        self.__foregroundColor = DEFAULT_TOAST_FOREGROUND_COLOR
        self.__backgroundColor = DEFAULT_TOAST_BACKGROUND_COLOR

    def __initUi(self, text):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # text in toast (toast foreground)
        self.__lbl = QLabel(text)
        self.__lbl.setObjectName("popupLbl")
        self.__lbl.setStyleSheet(
            f"QLabel#popupLbl {{ color: {self.__foregroundColor}; padding: 5px; }}"
        )

        self.__lbl.setMinimumWidth(
            min(200, self.__lbl.fontMetrics().boundingRect(text).width() * 2)
        )
        self.__lbl.setMinimumHeight(
            self.__lbl.fontMetrics().boundingRect(text).height() * 2
        )
        self.__lbl.setWordWrap(True)

        # toast background
        lay = QHBoxLayout()
        lay.addWidget(self.__lbl)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.setStyleSheet(
            f"QWidget {{ background: {self.__backgroundColor}; border-radius: 5px; }}"
        )
        self.__setToastSizeBasedOnTextSize()
        self.setLayout(lay)

        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # animation
        self.__initAnimation()

    def __initAnimation(self):
        self.__animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.__animation.setStartValue(0.0)
        self.__animation.setDuration(200)
        self.__animation.setEndValue(self.__opacity)

    def __initTimeout(self):
        self.__timer = QTimer(self)
        self.__timer_to_wait = self.__duration
        self.__timer.setInterval(1000)
        self.__timer.timeout.connect(self.__changeContent)
        self.__timer.start()

    def __changeContent(self):
        self.__timer_to_wait -= 1
        if self.__timer_to_wait <= 0:
            self.__animation.setDirection(QAbstractAnimation.Backward)
            self.__animation.start()
            self.__timer.stop()

    def setPosition(self, pos):
        geo = self.geometry()
        geo.moveCenter(pos)
        self.setGeometry(geo)

    def setAlignment(self, alignment):
        self.__lbl.setAlignment(alignment)

    def show(self):
        if self.__timer.isActive():
            pass
        else:
            self.__animation.setDirection(QAbstractAnimation.Forward)
            self.__animation.start()
            self.raise_()
            self.__initTimeout()
        return super().show()

    def isVisible(self) -> bool:
        return self.__timer.isActive()

    def setFont(self, font: QFont):
        self.__lbl.setFont(font)
        self.__setToastSizeBasedOnTextSize()

    def __setToastSizeBasedOnTextSize(self):
        self.setFixedWidth(self.__lbl.sizeHint().width() * 2)
        self.setFixedHeight(self.__lbl.sizeHint().height() * 2)

    def setDuration(self, duration: int):
        self.__duration = duration
        self.__initAnimation()  # Update animation after changing duration

    def setForegroundColor(self, color: QColor):
        if isinstance(color, str):
            color = QColor(color)
        self.__foregroundColor = color.name()
        self.__setForegroundColor()

    def setBackgroundColor(self, color: QColor):
        if isinstance(color, str):
            color = QColor(color)
        self.__backgroundColor = color.name()
        self.__setBackgroundColor()

    def __setForegroundColor(self):
        self.__lbl.setStyleSheet(
            f"QLabel#popupLbl {{ color: {self.__foregroundColor}; padding: 5px; }}"
        )

    def __setBackgroundColor(self):
        self.setStyleSheet(
            f"QWidget {{ background-color: {self.__backgroundColor}; border-radius: 5px; }}"
        )

    def setOpacity(self, opacity: float):
        self.__opacity = opacity
        self.__animation.setEndValue(self.__opacity)

    def eventFilter(self, obj, e) -> bool:
        if e.type() == 14:
            self.setPosition(
                QPoint(
                    self.__parent.rect().center().x(), self.__parent.rect().center().y()
                )
            )
        elif isinstance(obj, Toast):
            if e.type() == 75:
                self.__setForegroundColor()
                self.__setBackgroundColor()
        return super().eventFilter(obj, e)
