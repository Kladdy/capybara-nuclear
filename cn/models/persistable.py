import os
import pathlib
from abc import ABC, abstractmethod
from typing import TypeVar

from mashumaro.mixins.yaml import DataClassYAMLMixin

from cn.log import logger

T = TypeVar("T")


class PersistableBase(ABC):
    @abstractmethod
    def save(self, file_path: str) -> None:
        pass

    @classmethod
    @abstractmethod
    def load(cls: T, file_path: str) -> T:
        pass

    @classmethod
    @abstractmethod
    def validate_file_path(cls, file_path: str) -> None:
        pass


class PersistableYAML(PersistableBase, DataClassYAMLMixin):
    def save(self, file_path: str | pathlib.Path) -> None:
        """Save a class instance to YAML

        Parameters
        ----------
        file_path : str
            The path to the file to write
        """
        self.validate_file_path(file_path)

        file_path_dirname = os.path.dirname(file_path)
        if file_path_dirname:
            os.makedirs(file_path_dirname, exist_ok=True)

        logger.debug(f"Saving {type(self)} to '{file_path}'")

        yaml_data = str(self.to_yaml())
        with open(file_path, "w") as f:
            f.write(yaml_data)

    @classmethod
    def load(cls: T, file_path: str | pathlib.Path) -> T:
        """Load a class instance from YAML

        Parameters
        ----------
        file_path : str
            The path to the file to read

        Returns
        -------
        any
            The deserialized object
        """

        logger.debug(f"Loading {cls} from '{file_path}'")

        with open(file_path, "rb") as f:
            data = f.read().decode("utf-8")

        return cls.from_yaml(data)  # type: ignore

    @classmethod
    def validate_file_path(cls, file_path: str | pathlib.Path | None) -> None:
        """Validate the file path

        Parameters
        ----------
        file_path : str
            The path to the file to write

        Raises
        ------
        ValueError
            If the file path is not a string or does not end with '.yaml'
        """
        if not isinstance(file_path, str) and not isinstance(file_path, pathlib.Path):
            raise ValueError(
                f"file_path must be a string or pathlib.Path object, not {type(file_path)}"
            )
        if not str(file_path).endswith(".yaml"):
            raise ValueError(f"file_path ('{file_path}') must end with '.yaml'")
