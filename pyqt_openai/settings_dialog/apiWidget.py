from __future__ import annotations

import os
import logging

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from pyqt_openai import DEFAULT_API_CONFIGS
from pyqt_openai.config_loader import CONFIG_MANAGER
from pyqt_openai.util.common import set_api_key
from pyqt_openai.widgets.linkLabel import LinkLabel


class ApiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__api_keys = []
        # Get the api keys from the conf file with the env var name
        for conf in DEFAULT_API_CONFIGS:
            _conf = {
                "display_name": conf["display_name"],
                "env_var_name": conf["env_var_name"],
                "api_key": CONFIG_MANAGER.get_general_property(conf["env_var_name"]),
                "manual_url": conf["manual_url"],
            }
            self.__api_keys.append(_conf)

    def __initUi(self):
        self.setWindowTitle("API Key")

        columns = ["Provider", "API Key", "Manual URL"]
        self.__tableWidget = QTableWidget()
        self.__tableWidget.setColumnCount(len(columns))
        self.__tableWidget.setHorizontalHeaderLabels(columns)
        self.__tableWidget.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.__tableWidget.verticalHeader().setVisible(False)

        for i, obj in enumerate(self.__api_keys):
            self.__tableWidget.insertRow(i)
            modelItem = QTableWidgetItem(obj["display_name"])
            # Make item not editable
            modelItem.setFlags(modelItem.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.__tableWidget.setItem(i, 0, modelItem)

            apiKeyLineEdit = QLineEdit(obj["api_key"])
            apiKeyLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.__tableWidget.setCellWidget(i, 1, apiKeyLineEdit)

            getApiKeyLbl = LinkLabel()
            getApiKeyLbl.setText("Link")
            getApiKeyLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            getApiKeyLbl.setUrl(obj["manual_url"])
            self.__tableWidget.setCellWidget(i, 2, getApiKeyLbl)

        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.setApiKeys)

        loadEnvBtn = QPushButton("Load from ENV")
        loadEnvBtn.clicked.connect(self.loadFromEnvironment)

        # Create horizontal layout for buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(loadEnvBtn)
        buttonLayout.addWidget(saveBtn)

        lay = QVBoxLayout()
        lay.addWidget(QLabel("API Key"))
        lay.addWidget(self.__tableWidget)
        lay.addLayout(buttonLayout)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self.setMinimumHeight(150)

    def loadFromEnvironment(self):
        """Load API keys from environment variables if fields are empty."""
        logging.info("Starting loadFromEnvironment")
        
        for i, conf in enumerate(self.__api_keys):
            env_var_name = conf["env_var_name"]
            line_edit = self.__tableWidget.cellWidget(i, 1)
            assert isinstance(line_edit, QLineEdit)  # Type check to ensure it's a QLineEdit
            
            current_value = line_edit.text().strip()
            env_value = os.environ.get(env_var_name, '')
            
            logging.info(f"Checking {env_var_name}:")
            logging.info(f"  Current field value: {'<empty>' if not current_value else '<has value>'}")
            logging.info(f"  Environment value: {repr(env_value)}")  # Use repr to show empty strings
            
            # Only fill if current field is empty and env var exists and has content
            if not current_value and env_value:
                logging.info(f"  Setting field for {env_var_name} with value: {repr(env_value)}")
                line_edit.setText(env_value)
            else:
                reason = 'Field not empty' if current_value else 'No env var or empty value'
                logging.info(f"  Skipping {env_var_name}: {reason}")

    def setApiKeys(self):
        """Dynamically get the api keys from the table widget."""
        logging.info("Starting setApiKeys")
        api_keys = {}
        for i in range(self.__tableWidget.rowCount()):
            line_edit = self.__tableWidget.cellWidget(i, 1)
            assert isinstance(line_edit, QLineEdit)  # Type check to ensure it's a QLineEdit
            env_var_name = self.__api_keys[i]["env_var_name"]
            value = line_edit.text().strip()
            api_keys[env_var_name] = value
            logging.info(f"Setting {env_var_name} with value: {repr(value)}")

        # Save the api keys to the conf file
        for k, v in api_keys.items():
            CONFIG_MANAGER.set_general_property(k, v)
            set_api_key(k, v)
            logging.info(f"Saved {k} to config and environment")
