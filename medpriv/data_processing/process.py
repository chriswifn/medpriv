from abc import ABC, abstractmethod
from medpriv.utils import File
from pandas import read_csv, DataFrame
from typing import Optional, Set
import mimetypes


class ProcessData(ABC):
    """Interface for processing Data."""

    @abstractmethod
    def process(self, file: File) -> Optional[DataFrame]:
        pass

    @abstractmethod
    def can_process(self, file: File) -> bool:
        pass


class ProcessCsvData(ProcessData):
    """Process CSV Data."""

    def process(self, file: File) -> Optional[DataFrame]:
        if not self.can_process(file):
            raise ValueError("Cannot process this file type.")

        try:
            data = read_csv(file.name, encoding="utf-8", sep=",")
            return data
        except Exception as e:
            print(f"Error processing csv file: {e}")

    def can_process(self, file: File) -> bool:
        (content_type, _) = mimetypes.guess_type(file.name)
        return content_type == "text/csv" or content_type == "application/vnd.ms-excel"


class FacadeProcess:
    """Factory for Processors."""

    def __init__(self) -> None:
        self.processors: Set[ProcessData] = set()

    def add_processor(self, processor: ProcessData) -> None:
        self.processors.add(processor)

    def process(self, file: File) -> Optional[DataFrame]:
        for processor in self.processors:
            if processor.can_process(file):
                return processor.process(file)

    def can_process(self, file: File) -> bool:
        return any(processor.can_process(file) for processor in self.processors)
