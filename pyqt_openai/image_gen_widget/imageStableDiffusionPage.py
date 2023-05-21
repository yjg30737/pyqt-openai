import os
import warnings

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from qtpy.QtCore import Signal, QThread, QSettings
from qtpy.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QFormLayout, QSpinBox, QComboBox, \
    QLabel, QPlainTextEdit
from stability_sdk import client

from pyqt_openai.notifier import NotifierWidget
from pyqt_openai.svgLabel import SvgLabel
from pyqt_openai.toast import Toast

# Our Host URL should not be prepended with "https" nor should it have a trailing slash.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'


class StableDiffusionThread(QThread):
    replyGenerated = Signal(bytes)
    errorGenerated = Signal(str)

    def __init__(self, answers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__answers = answers

    def run(self):
        try:
            for resp in self.__answers:
                for artifact in resp.artifacts:
                    if artifact.finish_reason == generation.FILTER:
                        warnings.warn(
                            "Your request activated the API's safety filters and could not be processed."
                            "Please modify the prompt and try again.")
                    if artifact.type == generation.ARTIFACT_IMAGE:
                        self.replyGenerated.emit(artifact.binary)
        except Exception as e:
            self.errorGenerated.emit(str(e))



class ImageStableDiffusionPage(QWidget):
    submitSd = Signal(bytes)
    notifierWidgetActivated = Signal()

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_struct = QSettings('pyqt_openai.ini', QSettings.IniFormat)

        self.__sampler_dict = {
            'SAMPLER_DDIM': generation.SAMPLER_DDIM,
            'SAMPLER_DDPM': generation.SAMPLER_DDPM,
            'SAMPLER_K_EULER': generation.SAMPLER_K_EULER,
            'SAMPLER_K_EULER_ANCESTRAL': generation.SAMPLER_K_EULER_ANCESTRAL,
            'SAMPLER_K_HEUN': generation.SAMPLER_K_HEUN,
            'SAMPLER_K_DPM_2': generation.SAMPLER_K_DPM_2,
            'SAMPLER_K_DPM_2_ANCESTRAL': generation.SAMPLER_K_DPM_2_ANCESTRAL,
            'SAMPLER_K_LMS': generation.SAMPLER_K_LMS,
            'SAMPLER_K_DPMPP_2S_ANCESTRAL': generation.SAMPLER_K_DPMPP_2S_ANCESTRAL,
            'SAMPLER_K_DPMPP_2M': generation.SAMPLER_K_DPMPP_2M,
            'SAMPLER_K_DPMPP_SDE': generation.SAMPLER_K_DPMPP_SDE,
        }

        self.__info_dict = {
            'height': '512',
            'width': '512',
            'steps': 30,
            'samples': 1,
            'cfg_scale': 7,
            'engine': 'stable-diffusion-xl-beta-v2-2-2',
            'sampler': 'k_dpmpp_2m',
            'seed': 0, # random
        }

    def __initUi(self):
        sdApiGrpBox = QGroupBox()
        sdApiGrpBox.setTitle('DreamStudio API')

        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setPlaceholderText('Write your DreamStudio API Key...')
        self.__apiLineEdit.textChanged.connect(self.__enableSubmitBtn)
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)

        whatIsDreamStudioLbl = SvgLabel()
        whatIsDreamStudioLbl.setSvgFile('ico/help.svg')
        whatIsDreamStudioLbl.setToolTip('DreamStudio is a service which make it enable anyone to access the image generation tool\n without the need for software installation, coding knowledge, or a heavy-duty local GPU.')

        lay = QHBoxLayout()
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(whatIsDreamStudioLbl)
        lay.setContentsMargins(0, 0, 0, 0)
        sdApiInputWidget = QWidget()
        sdApiInputWidget.setLayout(lay)

        apiNoteLbl = QLabel('※ The validity of the API will be checked when you submit the form below.')

        lay = QVBoxLayout()
        lay.addWidget(sdApiInputWidget)
        lay.addWidget(apiNoteLbl)
        sdApiGrpBox.setLayout(lay)

        self.__modelCmbBox = QComboBox()
        self.__modelCmbBox.addItems([
            'stable-diffusion-v1',
            'stable-diffusion-v1-5',
            'stable-diffusion-512-v2-0',
            'stable-diffusion-768-v2-0',
            'stable-diffusion-512-v2-1',
            'stable-diffusion-768-v2-1',
            'stable-diffusion-xl-beta-v2-2-2',
            'stable-inpainting-v1-0',
            'stable-inpainting-512-v2-0',
        ])
        self.__modelCmbBox.setCurrentText(self.__info_dict['engine'])

        self.__upscaleEngineCmbBox = QComboBox()
        self.__upscaleEngineCmbBox.addItems([
            'esrgan-v1-x2plus', # cheap one
            'stable-diffusion-x4-latent-upscaler',
        ])

        self.__samplesSpinBox = QSpinBox()
        self.__samplesSpinBox.setRange(1, 10)
        self.__samplesSpinBox.setValue(self.__info_dict['samples'])
        # self.__samplesSpinBox.valueChanged.connect(self.__nChanged)

        self.__widthCmbBox = QComboBox()
        self.__widthCmbBox.addItems(['512', '768'])
        self.__widthCmbBox.setCurrentText(self.__info_dict['width'])

        self.__heightCmbBox = QComboBox()
        self.__heightCmbBox.addItems(['512', '768'])
        self.__heightCmbBox.setCurrentText(self.__info_dict['height'])

        self.__stepsSpinBox = QSpinBox()
        self.__stepsSpinBox.setRange(10, 150)
        self.__stepsSpinBox.setValue(self.__info_dict['steps'])

        self.__seedSpinBox = QSpinBox()
        self.__seedSpinBox.setValue(self.__info_dict['seed'])

        self.__cfgScalesSpinBox = QSpinBox()
        self.__cfgScalesSpinBox.setRange(1, 35)
        self.__cfgScalesSpinBox.setValue(self.__info_dict['cfg_scale'])

        self.__samplerCmbBox = QComboBox()
        self.__samplerCmbBox.addItems(list(self.__sampler_dict.keys()))
        self.__samplerCmbBox.setCurrentText(self.__info_dict['sampler'])

        self.__promptWidget = QPlainTextEdit()
        self.__submitBtn = QPushButton('Submit')
        self.__submitBtn.clicked.connect(self.__submit)
        self.__submitBtn.setEnabled(False)

        lay = QFormLayout()
        lay.addRow('Model', self.__modelCmbBox)
        lay.addRow('Samples', self.__samplesSpinBox)
        lay.addRow('Width', self.__widthCmbBox)
        lay.addRow('Height', self.__heightCmbBox)
        lay.addRow('Steps', self.__stepsSpinBox)
        lay.addRow('Seed', self.__seedSpinBox)
        lay.addRow('CFG scales', self.__cfgScalesSpinBox)
        lay.addRow('Sampler', self.__samplerCmbBox)
        lay.addRow(QLabel('Prompt'))
        lay.addRow(self.__promptWidget)

        generalGrpBox = QGroupBox('General')
        generalGrpBox.setLayout(lay)

        lay = QFormLayout()
        lay.addRow('Upscaling Model', self.__upscaleEngineCmbBox)
        advancedGrpBox = QGroupBox('Advanced (Working)')
        advancedGrpBox.setLayout(lay)
        advancedGrpBox.setEnabled(False)

        lay = QVBoxLayout()
        lay.addWidget(sdApiGrpBox)
        lay.addWidget(generalGrpBox)
        lay.addWidget(advancedGrpBox)
        lay.addWidget(self.__submitBtn)

        self.setLayout(lay)

        self.__loadApiKeyInIni()

    def __enableSubmitBtn(self):
        f = self.__apiLineEdit.text().strip() != ''
        self.__submitBtn.setEnabled(self.__apiLineEdit.text().strip() != '')
        if f:
            self.__settings_struct.setValue('SD_API_KEY', self.__apiLineEdit.text().strip())

    def __loadApiKeyInIni(self):
        # this api key should be yours
        if self.__settings_struct.contains('SD_API_KEY'):
            self.__apiLineEdit.setText(self.__settings_struct.value('SD_API_KEY'))
        else:
            self.__settings_struct.setValue('SD_API_KEY', '')

    def __submit(self):
        stability_api = client.StabilityInference(
            key=self.__apiLineEdit.text(),  # API Key reference.
            # upscale_engine=self.__upscaleEngineCmbBox.currentText(),
            verbose=True,  # Print debug messages.
            engine=self.__modelCmbBox.currentText(),  # Set the engine to use for generation.
            # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
            # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0
        )

        # Set up our initial generation parameters.
        answers = stability_api.generate(
            prompt=self.__promptWidget.toPlainText(),
            seed=self.__seedSpinBox.value(),  # If a seed is provided, the resulting generated image will be deterministic.
            # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
            # Note: This isn't quite the case for CLIP Guided generations, which we tackle in the CLIP Guidance documentation.
            steps=self.__stepsSpinBox.value(),  # Amount of inference steps performed on image generation. Defaults to 30.
            cfg_scale=self.__cfgScalesSpinBox.value(),  # Influences how strongly your generation is guided to match your prompt.
            # Setting this value higher increases the strength in which it tries to match your prompt.
            # Defaults to 7.0 if not specified.
            width=int(self.__widthCmbBox.currentText()),  # Generation width, defaults to 512 if not included.
            height=int(self.__heightCmbBox.currentText()),  # Generation height, defaults to 512 if not included.
            samples=self.__samplesSpinBox.value(),  # Number of images to generate, defaults to 1 if not included.
            sampler=self.__samplerCmbBox.currentText()  # Choose which sampler we want to denoise our generation with.
            # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
            # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        )

        self.__t = StableDiffusionThread(answers)
        self.__submitBtn.setEnabled(False)
        self.__t.start()
        self.__t.replyGenerated.connect(self.__afterGenerated)
        self.__t.errorGenerated.connect(self.__failToGenerate)

    def __failToGenerate(self, e):
        toast = Toast(text=e, duration=3, parent=self)
        toast.show()
        self.__submitBtn.setEnabled(True)

    def __afterGenerated(self, image_bin):
        self.submitSd.emit(image_bin)
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text='Response 👌', detailed_text='Click this!')
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.notifierWidgetActivated)
        self.__submitBtn.setEnabled(True)
