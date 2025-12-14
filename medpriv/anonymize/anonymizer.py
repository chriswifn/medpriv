from abc import ABC, abstractmethod
from medpriv.data_processing import Data


class Anonymizer(ABC):
    """Interface for anonymization strategies."""

    def __init__(self, data: Data):
        self.data = data

    @abstractmethod
    def anonymize(self) -> None:
        pass
