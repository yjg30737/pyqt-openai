from PySide6.QtWidgets import QWidget, QComboBox, QFormLayout, QDoubleSpinBox, QGroupBox, QVBoxLayout, QSpinBox, \
    QCheckBox, QLabel

from pyqt_openai import WHISPER_TTS_VOICE_TYPE, WHISPER_TTS_VOICE_SPEED_RANGE, EDGE_TTS_VOICE_TYPE
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.lang.translations import LangClass


class VoiceSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.voice_provider = CONFIG_MANAGER.get_general_property("voice_provider")
        self.voice = CONFIG_MANAGER.get_general_property("voice")
        self.speed = CONFIG_MANAGER.get_general_property("voice_speed")
        self.auto_play = CONFIG_MANAGER.get_general_property("auto_play_voice")
        self.auto_stop_silence_duration = CONFIG_MANAGER.get_general_property("auto_stop_silence_duration")

    def __initUi(self):
        ttsGrpBox = QGroupBox("Text to Speech")

        self.__voiceProviderCmbBox = QComboBox()
        self.__voiceProviderCmbBox.addItems(['OpenAI', 'edge-tts'])
        # self.__voiceProviderCmbBox.setCurrentText(self.voice_provider)
        self.__voiceProviderCmbBox.currentTextChanged.connect(self.__voiceProviderChanged)

        self.__warningLbl = QLabel("You need to install <b>mpv</b> to use edge-tts.")
        self.__warningLbl.setStyleSheet("color: yellow;")
        self.__warningLbl.setVisible(self.voice_provider == 'edge-tts')

        detailsGroupBox = QGroupBox("Details")

        self.__voiceCmbBox = QComboBox()
        self.__voiceCmbBox.addItems(WHISPER_TTS_VOICE_TYPE)
        self.__voiceCmbBox.setCurrentText(self.voice)

        self.__speedSpinBox = QDoubleSpinBox()
        self.__speedSpinBox.setRange(*WHISPER_TTS_VOICE_SPEED_RANGE)
        self.__speedSpinBox.setSingleStep(0.1)
        self.__speedSpinBox.setValue(float(self.speed))

        # Auto-Play voice when response is received
        self.__autoPlayChkBox = QCheckBox("Auto-Play Voice when Response is Received")
        # self.__autoPlayChkBox.setChecked(self.auto_play)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS["Voice"], self.__voiceCmbBox)
        lay.addRow(LangClass.TRANSLATIONS["Voice Speed"], self.__speedSpinBox)
        lay.addRow(self.__autoPlayChkBox)
        detailsGroupBox.setLayout(lay)

        lay = QFormLayout()
        lay.addRow(LangClass.TRANSLATIONS["Voice Provider"], self.__voiceProviderCmbBox)
        lay.addRow(self.__warningLbl)
        lay.addRow(detailsGroupBox)

        ttsGrpBox.setLayout(lay)

        sttGrpBox = QGroupBox("Speech to Text")

        # Allow user to determine Auto-Stop Silence Duration
        autoStopSilenceDurationSpinBox = QSpinBox()
        autoStopSilenceDurationSpinBox.setRange(3, 10)
        # autoStopSilenceDurationSpinBox.setValue(self.auto_stop_silence_duration)

        lay = QFormLayout()
        lay.addRow("Auto-Stop Silence Duration", autoStopSilenceDurationSpinBox)

        sttGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(ttsGrpBox)
        lay.addWidget(sttGrpBox)

        self.setLayout(lay)

    def getParam(self):
        return {
            "voice_provider": self.__voiceProviderCmbBox.currentText(),
            "voice": self.__voiceCmbBox.currentText(),
            "voice_speed": self.__speedSpinBox.value(),
            "auto_play_voice": self.__autoPlayChkBox.isChecked(),
            "auto_stop_silence_duration": self.__autoStopSilenceDurationSpinBox.value(),
        }

    def __voiceProviderChanged(self, text):
        f = text == 'OpenAI'
        if f:
            self.__voiceCmbBox.clear()
            self.__voiceCmbBox.addItems(WHISPER_TTS_VOICE_TYPE)
        else:
            self.__voiceCmbBox.clear()
            self.__voiceCmbBox.addItems(EDGE_TTS_VOICE_TYPE)
        self.__warningLbl.setVisible(not f)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = VoiceSettingsWidget()
    widget.show()
    sys.exit(app.exec())
