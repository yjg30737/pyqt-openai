from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtCore import QEasingCurve, QPropertyAnimation
from qtpy.QtWidgets import QGraphicsOpacityEffect, QPushButton

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


class AnimationButton(QPushButton):
    def __init__(
        self,
        text: str = "Other API",
        duration: int = 1000,
        start_value: float = 1,
        end_value: float = 0.5,
        parent: QWidget | None = None,
    ):
        super().__init__(text, parent)

        # Apply an opacity effect to the button
        self.opacity_effect: QGraphicsOpacityEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        # Create the animation for the opacity effect
        self.opacity_animation: QPropertyAnimation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(
            duration,
        )  # Duration of one animation cycle (in milliseconds)
        self.opacity_animation.setStartValue(start_value)  # Start with full opacity
        self.opacity_animation.setEndValue(end_value)  # End with lower opacity
        self.opacity_animation.setEasingCurve(
            QEasingCurve.Type.InOutQuad,
        )  # Smooth transition

        # Set the animation to alternate between fading in and out
        self.opacity_animation.setDirection(
            QPropertyAnimation.Direction.Forward,
        )  # Start direction

        # Connect the animation's finished signal to reverse direction
        self.opacity_animation.finished.connect(self.reverse_animation_direction)

        # Start the animation
        self.opacity_animation.start()

    def reverse_animation_direction(self):
        # Reverse the direction of the animation each time it finishes
        if self.opacity_animation.direction() == QPropertyAnimation.Direction.Forward:
            self.opacity_animation.setDirection(QPropertyAnimation.Direction.Backward)
        else:
            self.opacity_animation.setDirection(QPropertyAnimation.Direction.Forward)
        self.opacity_animation.start()
