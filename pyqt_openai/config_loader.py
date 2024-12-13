from __future__ import annotations

import os
import logging
import yaml
from typing import Union

from pyqt_openai import CONFIG_DATA, DEFAULT_API_CONFIGS, INI_FILE_NAME, get_config_directory

_config_cache: dict[str, dict[str, str]] | None = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_value(value: str) -> Union[bool, int, float, str]:
    # Boolean conversion
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    # Numeric conversion
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            pass
    # Default: return the value as is (string)
    return value


def convert_list(value: str) -> list[str]:
    # Convert comma-separated string to list
    return [item.strip() for item in value.split(",")]


def init_yaml() -> None:
    logger.info("Initializing YAML configuration")
    yaml_data: dict[str, dict[str, str]] = CONFIG_DATA  # type: ignore[assignment]

    config_dir: str = get_config_directory()
    config_path: str = os.path.join(config_dir, INI_FILE_NAME)
    logger.info(f"Config path: {config_path}")

    if not os.path.exists(config_path):
        logger.info("Config file does not exist, creating new one")
        # Save as YAML file
        with open(config_path, "w") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False)
    else:
        logger.info("Loading existing config file")
        with open(config_path) as yaml_file:
            prev_yaml_data: dict[str, dict[str, str]] = yaml.safe_load(yaml_file)
        # Add new keys
        for section, values in yaml_data.items():
            if section not in prev_yaml_data:
                logger.info(f"Adding new section: {section}")
                prev_yaml_data[section] = values
            else:
                for key, value in values.items():
                    if key not in prev_yaml_data[section]:
                        logger.info(f"Adding new key in {section}: {key}")
                        prev_yaml_data[section][key] = value
        # Save as YAML file
        with open(config_path, "w") as yaml_file:
            yaml.dump(prev_yaml_data, yaml_file, default_flow_style=False)


class ConfigManager:
    def __init__(
        self,
        yaml_file: str = INI_FILE_NAME,
    ) -> None:
        self.yaml_file: str = yaml_file
        logger.info(f"Initializing ConfigManager with file: {yaml_file}")
        self.config: dict[str, dict[str, str]] = self._load_yaml()

    def _load_yaml(self) -> dict[str, dict[str, str]]:
        logger.info(f"Loading YAML file: {self.yaml_file}")
        with open(self.yaml_file) as file:
            return yaml.safe_load(file)

    def _save_yaml(self):
        logger.info(f"Saving YAML file: {self.yaml_file}")
        with open(self.yaml_file, "w") as file:
            yaml.safe_dump(self.config, file)

    # Getter methods
    def get_dalle(self) -> dict[str, str]:
        return self.config.get("DALLE", {})

    def get_general(self) -> dict[str, str]:
        return self.config.get("General", {})

    def get_replicate(self) -> dict[str, str]:
        return self.config.get("REPLICATE", {})

    def get_g4f_image(self) -> dict[str, str]:
        return self.config.get("G4F_IMAGE", {})

    def get_dalle_property(self, key: str) -> str | None:
        return self.config.get("DALLE", {}).get(key)

    def get_general_property(self, key: str) -> str | None:
        value = self.config.get("General", {}).get(key)
        logger.info(f"Getting general property {key}: {repr(value)}")
        return value

    def get_replicate_property(self, key: str) -> str | None:
        return self.config.get("REPLICATE", {}).get(key)

    def get_g4f_image_property(self, key: str) -> str | None:
        return self.config.get("G4F_IMAGE", {}).get(key)

    # Setter methods
    def set_dalle_property(self, key: str, value: str) -> None:
        if "DALLE" not in self.config:
            self.config["DALLE"] = {}
        self.config["DALLE"][key] = value
        self._save_yaml()

    def set_general_property(self, key: str, value: str) -> None:
        logger.info(f"Setting general property {key} with value: {repr(value)}")
        if "General" not in self.config:
            self.config["General"] = {}
        self.config["General"][key] = value
        self._save_yaml()

    def set_replicate_property(self, key: str, value: str) -> None:
        if "REPLICATE" not in self.config:
            self.config["REPLICATE"] = {}
        self.config["REPLICATE"][key] = value
        self._save_yaml()

    def set_g4f_image_property(self, key: str, value: str) -> None:
        if "G4F_IMAGE" not in self.config:
            self.config["G4F_IMAGE"] = {}
        self.config["G4F_IMAGE"][key] = value
        self._save_yaml()


def update_api_key(yaml_file_path: str) -> None:
    logger.info(f"Updating API keys in: {yaml_file_path}")
    with open(yaml_file_path) as file:
        data: dict[str, dict[str, str]] = yaml.safe_load(file)

    # Rename API_KEY to OPENAI_API_KEY
    if "General" in data and "API_KEY" in data["General"]:
        value = data["General"].pop("API_KEY")
        logger.info(f"Converting API_KEY to OPENAI_API_KEY: {repr(value)}")
        data["General"]["OPENAI_API_KEY"] = value

    # Rename CLAUDE_API_KEY to ANTHROPIC_API_KEY
    if "General" in data and "CLAUDE_API_KEY" in data["General"]:
        value = data["General"].pop("CLAUDE_API_KEY")
        logger.info(f"Converting CLAUDE_API_KEY to ANTHROPIC_API_KEY: {repr(value)}")
        data["General"]["ANTHROPIC_API_KEY"] = value
        if value:  # Only set if value is not empty
            os.environ["ANTHROPIC_API_KEY"] = value

    # REPLICATE_API_TOKEN IS USED IN REPLICATE PACKAGE.
    # REPLICATE_API_KEY IS USED IN LITELLM.
    if "REPLICATE" in data and "REPLICATE_API_TOKEN" in data["REPLICATE"]:
        value = data["REPLICATE"]["REPLICATE_API_TOKEN"]
        logger.info(f"Setting REPLICATE_API_KEY from REPLICATE_API_TOKEN: {repr(value)}")
        if value:  # Only set if value is not empty
            os.environ["REPLICATE_API_KEY"] = value

    with open(yaml_file_path, "w") as file:
        yaml.safe_dump(data, file)


def load_api_keys() -> None:
    logger.info("Loading API keys from config to environment")
    env_vars: list[str] = [item["env_var_name"] for item in DEFAULT_API_CONFIGS]
    logger.info(f"Environment variables to load: {env_vars}")

    # Set API keys
    general_config = CONFIG_MANAGER.get_general()
    logger.info(f"Current general config keys: {list(general_config.keys())}")
    
    for key, value in general_config.items():
        if key in env_vars and value:  # Only set if value is not empty
            logger.info(f"Setting environment variable {key}: {repr(value)}")
            os.environ[key] = value
            logger.info(f"Environment now has {key}: {key in os.environ}")
        elif key in env_vars:
            logger.info(f"Skipping empty value for {key}")


init_yaml()
update_api_key(INI_FILE_NAME)
CONFIG_MANAGER = ConfigManager()
load_api_keys()
