import pandas as pd
from .anonymizer import Anonymizer
from medpriv.data_processing import KAnonymityData
from medpriv.utils import get_dimension_range, get_dimension_values, calculate_median
from typing import Any, Union, Tuple


class KAnonymityAnonymizer(Anonymizer):
    """K-Anonymity."""

    def __init__(self, k: int, data: KAnonymityData):
        super().__init__(data)
        self.k = k
        self.partitions = []

    def compute_initial_k_anonymity(self) -> int:
        """Calculate the k-anonymity of the input data based on the provided quasi-identifiers.

        Returns:
            int: The k-anonymity value of the dataset.
        """
        quasi_identifiers = [q if isinstance(q, str) else q["quid"] for q in self.data.quasiIdentifiers]
        group_sizes = self.data.inputData.groupby(quasi_identifiers).size()
        initial_k_anonymity = group_sizes.min()

        return initial_k_anonymity

    def compute_anonymized_k_anonymity(self) -> int:
        """Calculate the k-anonymity of the generalized partitions.

        Returns:
            int: The k-anonymity value of the generalized partitions.
        """
        all_partitions = pd.concat(self.partitions)
        quasi_identifiers = [q if isinstance(q, str) else q["quid"] for q in self.data.quasiIdentifiers]
        group_sizes = all_partitions.groupby(quasi_identifiers).size()
        anonymized_k_anonymity = group_sizes.min()

        return anonymized_k_anonymity

    def sort_by_quasi_identifier(self, quasi_identifier: str) -> None:
        """Sorts the input data based on the specified quasi-identifier.

        Args:
            quasi_identifier (str): The quasi-identifier (column name) to sort by.
        """
        self.data.inputData.sort_values(by=quasi_identifier, inplace=True)

    def select_dimension_for_split(self, examined_qi_index: int) -> str:
        """Chooses the dimension (quasi-identifier) to be examined based on its range.

        Args:
            examined_qi_index (int): The index of the quasi-identifier to be examined.

        Returns:
            str: The name of the chosen quasi-identifier.
        """
        quasi_identifiers = [q if isinstance(q, str) else q["quid"] for q in self.data.quasiIdentifiers]
        dimension_ranges = {q: get_dimension_range(self.data.inputData[q]) for q in quasi_identifiers}
        sorted_dimensions = sorted(dimension_ranges.items(), key=lambda x: x[1], reverse=True)
        return sorted_dimensions[examined_qi_index][0]

    def determine_most_improtant_quifs(self):
        """Sort the Quasi-Identifiers from most to least information-bearing.

        Returns:
            A sorted list of quasi identifiers.
        """
        sorted_quifs = []
        tuples = []
        temp_data = self.data.inputData.copy()
        for i in self.data.quasiIdentifiers:
            temp_data.sort_values(by=i)
            local_list = []
            for j in temp_data[i].unique():
                grouped = temp_data.groupby(temp_data[i])
                temp_table = grouped.get_group(j)
                local_list.append(temp_table)
            k = len(local_list)
            tuples.append((k, i))
        tuples.sort(reverse=True)
        for x in tuples:
            sorted_quifs.append(x[1])
        return sorted_quifs

    def anonymize(self) -> None:
        """Anonymizes the data by applying k-anonymity and generalizing the partitions."""
        self.anonymize_partition(self.data.inputData)
        self.generalize_partitions()

    def anonymize_partition(self, partition: pd.DataFrame, examined_qi_index: int = 0) -> None:
        """Recursively partitions and anonymizes the data based on k-anonymity.

        Args:
            partition (pd.DataFrame): The current partition of data to be anonymized.
            examined_qi_index (int, optional): The index of the current quasi-identifier.
        """
        if len(partition) <= 2 * self.k or examined_qi_index == len(self.data.quasiIdentifiers):
            self.partitions.append(partition)
            return

        dimension = self.select_dimension_for_split(examined_qi_index)
        dimension_values = get_dimension_values(partition, dimension)
        split_value = calculate_median(dimension_values)
        split_partitions = self.split_partition(partition, dimension, split_value)

        if split_partitions:
            self.anonymize_partition(split_partitions[0])
            self.anonymize_partition(split_partitions[1])
        else:
            self.anonymize_partition(partition, examined_qi_index + 1)

    def split_partition(
        self, partition: pd.DataFrame, dimension: str, split_value: Any
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], None]:
        """Splits a partition into two based on a split value for a given dimension.

        Args:
            partition (pd.DataFrame): The data partition to be split.
            dimension (str): The dimension (column name) on which to split the partition.
            split_value (float): The value used to split the partition into two.

        Returns:
            tuple: A tuple containing the two split dataframes.
        """
        left_partition = partition[partition[dimension] <= split_value]
        right_partition = partition[partition[dimension] > split_value]

        if len(left_partition) < self.k or len(right_partition) < self.k:
            return None

        return left_partition, right_partition

    def generalize_partitions(self) -> None:
        """Generalizes the quasi-identifiers in each partition based on their ranges or decoding maps."""
        generalized_partitions = []
        for partition in self.partitions:
            generalized_partition = partition.copy()
            for qi in self.data.quasiIdentifiers:
                quasiIdentifier = qi if isinstance(qi, str) else qi["quid"]

                min_val, max_val = (
                    generalized_partition[quasiIdentifier].min(),
                    generalized_partition[quasiIdentifier].max(),
                )
                if quasiIdentifier in self.data.decoding:
                    unique_vals = sorted(generalized_partition[quasiIdentifier].unique())
                    generalized_vals = "#".join([self.data.decoding[quasiIdentifier][val] for val in unique_vals])
                    generalized_partition[quasiIdentifier] = generalized_vals
                else:
                    generalized_partition[quasiIdentifier] = f"{min_val}#{max_val}" if min_val != max_val else min_val

            generalized_partitions.append(generalized_partition)
        self.partitions = generalized_partitions
