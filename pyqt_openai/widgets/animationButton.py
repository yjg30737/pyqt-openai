from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsOpacityEffect, QPushButton


class AnimationButton(QPushButton):
    def __init__(self, text='Other API', duration=1000, start_value=1, end_value=0.5,
                 parent=None):
        super().__init__(text, parent)

        # Apply an opacity effect to the button
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        # Create the animation for the opacity effect
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)  # Duration of one animation cycle (in milliseconds)
        self.animation.setStartValue(start_value)  # Start with full opacity
        self.animation.setEndValue(end_value)  # End with lower opacity
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Smooth transition

        # Set the animation to alternate between fading in and out
        self.animation.setDirection(QPropertyAnimation.Direction.Forward)  # Start direction

        # Connect the animation's finished signal to reverse direction
        self.animation.finished.connect(self.reverse_animation_direction)

        # Start the animation
        self.animation.start()

    def reverse_animation_direction(self):
        # Reverse the direction of the animation each time it finishes
        if self.animation.direction() == QPropertyAnimation.Direction.Forward:
            self.animation.setDirection(QPropertyAnimation.Direction.Backward)
        else:
            self.animation.setDirection(QPropertyAnimation.Direction.Forward)
        self.animation.start()