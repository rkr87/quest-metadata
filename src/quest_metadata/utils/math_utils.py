"""
math_utils.py

This module provides utility functions for math calculations.

Functions:
    - percentile(values: list[int] | list[float], n: Annotated[int]) -> float:
        Convert a string to snake_case.

Usage:
    To use these functions, import the module and call the desired
    function as follows:

    ```python
    from math_utils import percentile

    lower_quartile = percentile([0,1,2,3], 25)
    ```
"""
from typing import Annotated

from annotated_types import Ge, Le


def percentile(
    values: list[int] | list[float],
    n: Annotated[int, Ge(0), Le(100)]
) -> float:
    """
    Compute the nth percentile of a list of values.

    Parameters:
    - values (list[int] | list[float]): A list of values for which the
        percentile is to be calculated.
    - n (Annotated[int]): The desired percentile value between 0 and 100.

    Returns:
    - float: The computed nth percentile of the input values.
    """
    sort: list[int] | list[float] = sorted(values)
    index: float = (n / 100) * (len(sort) - 1)
    if index.is_integer():
        return sort[int(index)]
    floor: int = int(index // 1)
    ceiling: int = floor + 1
    fraction: float = index - floor
    return sort[floor] + fraction * (sort[ceiling] - sort[floor])
