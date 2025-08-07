import subprocess
from qtpy.QtCore import QThread, Signal
from qtpy.QtWidgets import (
    QDialog,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QWidget,
    QTextBrowser,
    QMessageBox,
)


class DownloadThread(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def run(self):
        cmd = ["ollama", "pull", self.model_name]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )

            for line in iter(process.stdout.readline, ""):
                if line:
                    self.log_signal.emit(line.rstrip())
            process.stdout.close()
            retcode = process.wait()
            success = retcode == 0
            self.finished_signal.emit(success)
        except Exception as e:
            self.log_signal.emit(f"Error: {e}")
            self.finished_signal.emit(False)


class DownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__download_thread = None
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('Download Ollama Model')
        self.setModal(True)

        self.modelLineEdit = QLineEdit()
        self.modelLineEdit.setPlaceholderText("ex: llama3.1:8b")

        self.downloadButton = QPushButton("Download")
        self.downloadButton.clicked.connect(self.onDownloadClicked)

        lay = QHBoxLayout()
        lay.addWidget(self.modelLineEdit)
        lay.addWidget(self.downloadButton)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.logBrowser = QTextBrowser()
        self.logBrowser.setStyleSheet(
            "background-color: black; color: white; font-family: monospace;"
        )

        mainLay = QVBoxLayout()
        mainLay.addWidget(topWidget)
        mainLay.addWidget(self.logBrowser)

        self.setLayout(mainLay)
        self.resize(600, 400)

    def onDownloadClicked(self):
        model_name = self.modelLineEdit.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Error", "Please enter a model name.")
            return

        self.logBrowser.clear()
        self.downloadButton.setEnabled(False)
        self.modelLineEdit.setEnabled(False)

        self.__download_thread = DownloadThread(model_name)
        self.__download_thread.log_signal.connect(self.appendLog)
        self.__download_thread.finished_signal.connect(self.downloadFinished)
        self.__download_thread.start()

    def appendLog(self, text):
        self.logBrowser.append(text)

    def getModelName(self):
        return self.modelLineEdit.text().strip() if self.modelLineEdit else ""

    def downloadFinished(self, success):
        self.downloadButton.setEnabled(True)
        self.modelLineEdit.setEnabled(True)

        if success:
            QMessageBox.information(
                self, "Download Complete", "Model download completed successfully."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, "Download Failed", "Model download failed. Check logs."
            )
