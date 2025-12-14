import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union


class Data(ABC):
    """Data interface."""

    def __init__(self, quasiIdentifiers: List[Any], inputData: pd.DataFrame):
        self.quasiIdentifiers = quasiIdentifiers
        self.inputData = inputData

    @abstractmethod
    def _prepare(self, quasiIdentifiers: List[Any]) -> None:
        """Prepare the Data for Anonymization.

        Attributes:
            quasi_identifiers (List[Any]): List of quasi-identifiers.
        """
        pass


class KAnonymityData(Data):
    """Represents a structure for handling input data, quasi-identifiers and identifiers.

    Attributes:
        encoding (Dict[str, Dict[str, int]]): Mapping of quasi-identifier values to encoded integer codes.
        decoding (Dict[str, Dict[int, str]]): Mapping of encoded integer codes to original quasi-identifiers.
        inputData (pd.DataFrame): The input data.
        quasiIdentifiers (List[Any]): List of quasi-identifiers.
        identifiers (List[str]): List of identifiers.
    """

    def __init__(
        self,
        inputData: pd.DataFrame,
        quasiIdentifiers: List[Any],
        identifiers: List[str],
    ):
        """Initializes the Data object and performs normalization and anonymization of identifiers.

        Args:
            inputData (pd.DataFrame): The input data
            quasiIdentifiers: (List[Any]: List of quasi-identifiers.
            identifiers (List[str]): List of identifiers.
        """
        self.identifiers = identifiers
        self.encoding: Dict[str, Dict[str, int]] = {}
        self.decoding: Dict[str, Dict[str, int]] = {}
        super().__init__(quasiIdentifiers, inputData)
        self._anonymize_identifiers(identifiers)
        self._prepare(quasiIdentifiers)

    def _can_categorize(self, column: str) -> Union[bool, None]:
        """Determines if the specified column can be categorized (non-numeric).

        Args:
            column (str): The name of the column to check.

        Returns:
            bool: True if the column can be categorized, False otherwise
        """
        try:
            first_value = self.inputData[column].iloc[0]
            if int(first_value) == first_value:
                return False
        except (ValueError, TypeError, IndexError):
            return True

    def _prepare(self, quasiIdentifiers: List[Any]) -> None:
        """Normalizes the values in quasi-identifiers by encoding them and handling redactions.

        Args:
            quasiIdentifiers (List[Any]): List of quasi-identifiers.
        """
        for qi in quasiIdentifiers:
            quasi_identifier = qi if isinstance(qi, str) else qi["quid"]
            redactions = qi.get("redactions", {}) if isinstance(qi, dict) else {}

            if not self._can_categorize(quasi_identifier):
                continue

            if redactions:
                self.inputData[quasi_identifier] = self.inputData[quasi_identifier].replace(redactions)
                continue

            # Convert to lowercase for case insensitivity
            self.inputData[quasi_identifier] = self.inputData[quasi_identifier].str.lower()

            # Get unique values and assign codes
            uniques = pd.Series(self.inputData[quasi_identifier].unique())
            # codes = uniques.rank(method="dense").astype(int) - 1
            codes = pd.Series(uniques).astype("category").cat.codes

            self.encoding[quasi_identifier] = dict(zip(uniques, codes))
            self.decoding[quasi_identifier] = dict(zip(codes, uniques))

            # Replace the values in the column with the corresponding codes
            self.inputData[quasi_identifier] = self.inputData[quasi_identifier].map(self.encoding[quasi_identifier])

    def _anonymize_identifiers(self, identifiers):
        """Anonymizes the specified identifiers by replacing their values with `*`.

        Args:
            identifiers (List[str]): List of identifiers to anonymize.
        """
        for identifier in identifiers:
            if identifier not in self.inputData.columns:
                continue

            self.inputData[identifier] = "*"


class EpsilonData(Data):
    """Represents a structure for handling input data, quasi-identifiers and identifiers.

    Attributes:
        encoding (Dict[str, Dict[str, int]]): Mapping of quasi-identifier values to encoded integer codes.
        decoding (Dict[str, Dict[int, str]]): Mapping of encoded integer codes to original quasi-identifiers.
        inputData (pd.DataFrame): The input data.
        quasiIdentifiers (List[Union[str, Dict[str, Union[str, Dict[str, str]]]]]): List of quasi-identifiers.
        identifiers (List[str]): List of identifiers.
    """

    def __init__(
        self,
        inputData: pd.DataFrame,
        quasiIdentifiers: List[Any],
    ):
        """Initializes the Data object and performs normalization and anonymization of identifiers.

        Args:
            inputData (pd.DataFrame): The input data
            quasiIdentifiers: (List[Union[str, Dict[str, Union[str, Dict[str, str]]]]]: List of quasi-identifiers.
            identifiers (List[str]): List of identifiers.
        """
        super().__init__(quasiIdentifiers, inputData)
        self.histogram: np.ndarray = np.array([])
        self.indexMapping: Dict[str, Dict[Any, int]] = {}
        self._prepare(quasiIdentifiers)

    def _prepare(self, quasiIdentifiers: List[str]) -> None:
        """Creates the histogram for epsilon differential privacy.

        Args:
            quasiIdentifiers (List[str]): List of quasi-identifiers.
        """
        # shape of n-dimensional array
        shape = [self.inputData[col].nunique() for col in quasiIdentifiers]

        # fill n-dimensional array with 0
        self.histogram = np.zeros(shape, dtype=int)

        # mapping unique values to indices
        self.index_mapping = {
            col: {val: i for i, val in enumerate(self.inputData[col].unique())} for col in quasiIdentifiers
        }

        # group by quasi-identifiers and count occurences
        grouped = self.inputData.groupby(list(quasiIdentifiers)).size().reset_index(name="count")

        # Populate the n-dimensional array with counts
        for _, row in grouped.iterrows():
            index = tuple(self.index_mapping[col][row[col]] for col in quasiIdentifiers)
            self.histogram[index] = row["count"]
