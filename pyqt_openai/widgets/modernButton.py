from PySide6.QtWidgets import QPushButton

from pyqt_openai.settings_dialog.settingsDialog import SettingsDialog


class ModernButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.clicked.connect(lambda _: SettingsDialog(default_index=1, parent=self).exec_())
        self.setStyleSheet('''
        QPushButton {
            background-color: #007BFF;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            font-family: "Arial";
            font-weight: bold;
            border: 2px solid #007BFF;
        }
        QPushButton:hover {
            background-color: #0056b3;
            border-color: #0056b3;
        }
        QPushButton:pressed {
            background-color: #003f7f;
            border-color: #003f7f;
        }
        '''
                                       )