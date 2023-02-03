"""Configuration file."""
import json
import os
from string import Template
from typing import AnyStr
from typing import Dict

import yaml
from attrs import asdict
from attrs import define
from attrs import field
from attrs import fields
from prompt_toolkit import PromptSession

from .base import Base


@define
class Authorization:
    """Contains settings for authorization to Graph API and Azure endpoints."""

    client_id: AnyStr = field(factory=str, metadata={"question": Template("Please provide your Graph API Client ID: ")})
    client_secret: AnyStr = field(
        factory=str, metadata={"question": Template("Please provide your Graph API Client Secret: ")}
    )
    tenant_id: AnyStr = field(factory=str, metadata={"question": Template("Please provide your Graph API Tenant ID: ")})
    subscription_id: AnyStr = field(
        factory=str, metadata={"question": Template("Please provide your Azure Sentinel Subscription ID: ")}
    )
    resource_group_name: AnyStr = field(
        factory=str, metadata={"question": Template("Please provide your Azure Sentinel Resource Group Name: ")}
    )
    workspace_name: AnyStr = field(
        factory=str, metadata={"question": Template("Please provide your Azure Sentinel Workspace Name: ")}
    )
    api_version: AnyStr = "2022-11-01"


@define
class Configuration:
    """The main configuration data model."""

    authorization: Authorization = field(factory=Authorization)

    def __attrs_post_init__(self):
        """Casting data objects to their correct type during initialization."""
        if self.authorization:
            self.authorization = Authorization(**self.authorization)


class ConfigurationManager(Base):
    """The main class used to manage retreiving and saving configuration files from disk."""

    CONFIG_PATH = "~/.config/sentinel-automation.yml"
    session = PromptSession()

    def __init__(self) -> None:
        """Determines if configuration file exists or not."""
        self.config_path = self._get_absolute_path(path=self.CONFIG_PATH)
        if not os.path.exists(self.config_path):
            self._save_to_disk(path=self.config_path, data=self._prompt())

    def _prompt(self) -> Dict[str, str]:
        """Prompts the user to enter values for the defined services in our Configuration data model.

        The questions are metadata within our Configuration data model using string Templates.

        Returns:
            Dict[str, str]: A dictionary of the provided answers to our configuration questions.
        """
        authorization = {
            "tenant_id": self.session.prompt(fields(Authorization).tenant_id.metadata["question"].substitute()),
            "client_id": self.session.prompt(fields(Authorization).client_id.metadata["question"].substitute()),
            "client_secret": self.session.prompt(fields(Authorization).client_secret.metadata["question"].substitute()),
            "subscription_id": self.session.prompt(
                fields(Authorization).subscription_id.metadata["question"].substitute()
            ),
            "resource_group_name": self.session.prompt(
                fields(Authorization).resource_group_name.metadata["question"].substitute()
            ),
            "workspace_name": self.session.prompt(
                fields(Authorization).workspace_name.metadata["question"].substitute()
            ),
        }
        return asdict(Configuration(authorization=authorization))

    def _read_from_disk(self, path: str) -> Dict[str, str]:
        """Retreives the configuration file values from a given path on the disk.

        Args:
            path (str): The path to the configuration file on disk.

        Raises:
            FileNotFoundError: Raises when the file cannot be found.
            IsADirectoryError: Raises when the provided path is a directory.

        Returns:
            Dict[str, str]: A dictionary containing the defined services keys and values.
        """
        if os.path.exists(path) and os.path.isfile(path):
            try:
                with open(path) as f:
                    if path.endswith(".json"):
                        return json.load(f)
                    elif path.endswith(".yml") or path.endswith(".yaml"):
                        return yaml.load(f, Loader=yaml.SafeLoader)
                    else:
                        raise FileNotFoundError(f"The provided path value '{path}' is not one of '.yml'.")
            except Exception as e:
                self.__logger.warning(f"The provided config file {path} is not in the correct format. {e}")
        elif os.path.isdir(path):
            raise IsADirectoryError(f"The provided path is a directory and must be a file: {path}")

    def _save_to_disk(self, path: str, data: Dict[str, str]) -> None:
        """Saves the provided configuration data to the provided path.

        Args:
            path (str): The path to save our configuration data.
            data (Dict[str, str]): The data to save within our configuration file.

        Raises:
            Exception: Raises when an unknown exception is made.
            FileNotFoundError: Raises when the file cannot be found.
            IsADirectoryError: Raises when the provided value is a directory.
        """
        try:
            if not os.path.exists(os.path.dirname(path)):
                try:
                    os.makedirs(os.path.dirname(path))
                except Exception as e:
                    message = f"Attempted to create the provided directories '{path}' but was unable to."
                    self.__logger.critical(message + e)
                    raise e
            with open(path, "w+") as f:
                if path.endswith(".json"):
                    json.dump(data, f)
                elif path.endswith(".yml") or path.endswith(".yaml"):
                    yaml.dump(data, f)
                else:
                    raise FileNotFoundError(f"The provided path value '{path}' is not one of '.yml'.")
        except IsADirectoryError as ie:
            raise ie
