import pandas as pd
from typing import List, Any, Union
import numpy as np


def get_dimension_values(partition: pd.DataFrame, dimension: str) -> List[Any]:
    """Extracts the set of values for a specific dimension from a partition.

    Args:
        partition(pd.DataFrame): The partition of data
        dimension (str): The dimension (column name) for which the frequency set is extracted

    Returns:
        list: A list of values from the dimension
    """
    return [value for value in partition[dimension]]


def calculate_median(values: List[Union[int, float, str]]) -> Union[int, float, str]:
    """Computes the median of a list of values that can be either numerical or strings.

    Args:
        values (List[Union[int, float, str]]): A list of numerical or string values.

    Returns:
        Union[int, float, str]: The median value of the list.
    """
    sorted_values = sorted(values)
    n = len(sorted_values)
    middle = n // 2

    if n % 2 == 0:  # If even number of values, return the average of the middle two
        median_left = sorted_values[middle - 1]
        median_right = sorted_values[middle]
        if isinstance(median_left, str) or isinstance(median_right, str):
            # For strings, return the left middle value
            return median_left
        else:
            # For numbers, return the average of the two middle values
            return (median_left + median_right) / 2
    else:
        return sorted_values[middle]


def get_dimension_range(values):
    """Calculates a range value that works for both strings and integers.

    Args:
        values (pd.Series): A Series of values from a dimension.

    Returns:
        int: A range value based on the sorted index positions of unique values.
    """
    unique_values = sorted(values.unique())
    range_value = len(unique_values) - 1
    return range_value


def concatenate_dataframes(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate a list of DataFrames into a single DataFrame.

    Args:
        dataframes (list of pd.DataFrame): A list of DataFrames to concatenate

    Returns:
        pd.DataFrame: The concatenated DataFrame
    """
    return pd.concat(dataframes)


def sample_geometric(alpha: float) -> int:
    """Sample from the two-sided geometric distribution with parameter alpha.

    Args:
        alpha (float): The parameter of the geometric distribution (0 < alpha < 1).

    Returns:
        int: A sample from the two-sided geometric distribution.
    """
    u = np.random.uniform(0, 1)
    x = np.floor(np.log(1 - u) / np.log(alpha))
    sign = -1 if np.random.uniform(0, 1) < 0.5 else 1
    # print(x)
    return sign * int(x)
