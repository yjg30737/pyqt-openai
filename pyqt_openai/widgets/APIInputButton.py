import colorsys

from PySide6.QtWidgets import QPushButton

from pyqt_openai.settings_dialog.settingsDialog import SettingsDialog


class APIInputButton(QPushButton):
    def __init__(self, base_color="#007BFF"):
        super().__init__()
        self.setObjectName("modernButton")
        self.base_color = base_color  # Default base color
        self.__initUi()

    def __initUi(self):
        self.clicked.connect(
            lambda _: SettingsDialog(default_index=1, parent=self).exec()
        )
        self.updateStylesheet(self.base_color)

    def updateStylesheet(self, base_color):
        """Generate dynamic styles based on the base color"""
        hover_color = self.adjust_brightness(base_color, 0.8)  # Brighten
        pressed_color = self.adjust_brightness(base_color, 0.6)  # Darken
        border_color = pressed_color  # Use the same color for border

        # Dynamically generated stylesheet
        self.setStyleSheet(
            f"""
            QPushButton#modernButton {{
                background-color: {base_color};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-family: "Arial";
                font-weight: bold;
                border: 2px solid {base_color};
            }}
            QPushButton#modernButton:hover {{
                background-color: {hover_color};
                border-color: {hover_color};
            }}
            QPushButton#modernButton:pressed {{
                background-color: {pressed_color};
                border-color: {border_color};
            }}
            """
        )

    def adjust_brightness(self, hex_color, factor):
        """Adjust the brightness of a given hex color"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Convert RGB to HLS
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

        # Adjust lightness
        l = max(0, min(1, l * factor))  # Ensure lightness stays within 0-1
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Convert RGB back to hex
        return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"
