from __future__ import annotations

from pyqt_openai.settings_dialog.settingsDialog import SettingsDialog
from pyqt_openai.widgets.featureButton import FeatureButton


class OllamaButton(FeatureButton):
    def __init__(
        self,
        base_color: str = "#007BFF",
    ):
        super().__init__(base_color)
        self.__initUi()

    def __initUi(self):
        self.clicked.connect(
            lambda _: SettingsDialog(default_index=1, parent=self).exec(),
        )
        self.updateStylesheet(self.base_color)
        self.setText('Manage Ollama Models')