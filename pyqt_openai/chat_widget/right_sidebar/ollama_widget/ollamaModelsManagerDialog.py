from qtpy.QtCore import QThread
from qtpy.QtWidgets import QListWidget
from qtpy.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QDialog,
)
from pyqt_openai.chat_widget.right_sidebar.ollama_widget.ollamaDownloadModelDialog import DownloadDialog
from pyqt_openai.util.common import get_ollama_model


class RemoveModelThread(QThread):
    def __init__(self, wrapper, models):
        super().__init__()
        self.__wrapper = wrapper
        self.__models = models

    def run(self):
        try:
            for model in self.__models:
                if self.__wrapper.model_exists(model):
                    self.__wrapper.remove_model(model)
                else:
                    print(f"Model {model} does not exist.")
        except Exception as e:
            print(f"Error: {e}")


class OllamaModelManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ollama Model Manager")
        self.setMinimumSize(400, 300)

        # Layout
        layout = QVBoxLayout(self)

        # Model List
        self.model_list = QListWidget(self)
        self.model_list.addItems(get_ollama_model(name_only=True))
        layout.addWidget(QLabel("Available Models:"))
        layout.addWidget(self.model_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Model", self)
        self.remove_button = QPushButton("Remove Model", self)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)

        # Connect buttons to methods
        self.add_button.clicked.connect(self.add_model)
        self.remove_button.clicked.connect(self.remove_model)

        # Count the number of models
        cnt = self.model_list.count()
        # Toggle the delete button based on model count
        self.remove_button.setEnabled(cnt > 0)

    def add_model(self):
        # Logic to add a model
        dialog = DownloadDialog()
        dialog.exec()
        if dialog.result() == QDialog.Accepted:
            model_name = dialog.modelLineEdit.text().strip()
            if model_name:
                self.model_list.addItem(model_name)

    def remove_model(self):
        # Logic to remove a model
        try:
            models = self.model_list.selectedItems()
            self.__t = RemoveModelThread(
                # Get the model names
                [item.text() for item in models]
            )
            self.__t.start()
            self.__t.finished.connect(self.remove_model_in_list)
        except Exception as e:
            print(f"Error removing model: {e}")

    def remove_model_in_list(self):
        for item in self.model_list.selectedItems():
            # Remove the selected item from the list
            self.model_list.takeItem(self.model_list.row(item))
