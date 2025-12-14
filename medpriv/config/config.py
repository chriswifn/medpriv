import json
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Union, Any, TypeVar, Generic
from medpriv.utils import File

T = TypeVar("T")


@dataclass
class BaseConfig(Generic[T]):
    """Base Data class to encapsulate common configuration parameters.

    Attributes:
        identifiers (List[str]): List of identifiers (identifiers that
          can be used to uniquely identify a person, e.g. name).
        quasiIdentifiers (List[T]): List of quasi identifiers
          (identifiers that in combination can be used to uniquely
          identify a person).
        inputFile (File): Path to the input CSV file.
        outputFile (File): Path to the output CSV file.
    """

    identifiers: List[str]
    quasiIdentifiers: List[T]
    inputFile: File = field(metadata={"serializer": File.to_dict, "deserializer": File.from_dict})
    outputFile: File = field(metadata={"serializer": File.to_dict, "deserializer": File.from_dict})

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        for field_ in self.__dataclass_fields__.values():
            if "serializer" in field_.metadata:
                result[field_.name] = field_.metadata["serializer"](getattr(self, field_.name))
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        for field_ in cls.__dataclass_fields__.values():
            if "deserializer" in field_.metadata:
                data[field_.name] = field_.metadata["deserializer"](data[field_.name])
        return cls(**data)


@dataclass
class KConfig(BaseConfig[Union[str, Dict]]):
    """Data Class to encapsulate to configuration parameters for k-anonymity.

    Attributes:
        k (int): The k value for k-anonymity.
    """

    k: int


@dataclass
class EpsilonConfig(BaseConfig[str]):
    """Data class to encapsulate configuration parameters for epsilon differential privacy.

    Attributes:
        epsilon (float): The epsilon value for differential privacy.
    """

    epsilon: float


class ConfigLoader:
    """Load and initialize configuration from a JSON file.

    Args:
        configFile (str): Path to the configuration file
    """

    def __init__(self, configFile: File):
        """Initialize the ConfigLoader.

        Args:
            configFile (str): Path to the configuration file represented as a String
        """
        self.configFile = configFile

    def load_config(self) -> Union[KConfig, EpsilonConfig]:
        """Load the configuration from a JSON file and return a Config dataclass.

        Returns:
            Config: Instance of Config dataclass with the
              values parsed from the Configuration file

        Raises:
            FileNotFoundError: If the configuration file is not found
            ValueError: If the configuration file cannot be decoded
              from JSON.
        """
        try:
            with open(self.configFile.name, "r") as file:
                configDict = json.load(file)
                return self._dict_to_config(configDict)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: {self.configFile.name} does not exist! {e}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Error: Json Decode failed! {e}")

    def _dict_to_config(self, configDict: Dict[str, Any]) -> Union[KConfig, EpsilonConfig]:
        """Helper function to convert a dictionary to a Config dataclass.

        Args:
            configDict (Dict[str, Any]): The configuration dictionary

        Returns:
            Config: An instance of Config
        """
        if "k" in configDict:
            # return KConfig(**configDict)
            return KConfig.from_dict(configDict)
        elif "epsilon" in configDict:
            # return EpsilonConfig(**configDict)
            return EpsilonConfig.from_dict(configDict)
        else:
            raise ValueError("Unknown configuration type in the JSON file.")

    def init_config(self, defaultConfig: Union[KConfig, EpsilonConfig]) -> None:
        """Initializes the configuration file with default values.

        Args:
            defaultConfig (Config): The default configuration (or a
              changed configuration)
        """
        with open(self.configFile.name, "w") as file:
            json.dump(defaultConfig.to_dict(), file, indent=4)
