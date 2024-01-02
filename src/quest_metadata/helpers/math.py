"""
Module providing a math based utility functions.

Functions:
- percentile: Function to calculate the nth percentile of a list of values.

Annotations:
- Annotated: Used for adding constraints to the function parameter.
"""
from typing import Annotated

from annotated_types import Ge, Le


def percentile(
    values: list[int] | list[float],
    n: Annotated[int, Ge(0), Le(100)]
) -> float:
    """
    Calculate the nth percentile of a list of values.

    Args:
    - values (list[int] | list[float]): The list of values.
    - n (Annotated[int, Ge(0), Le(100)]): The percentile to calculate
        (between 0 and 100).

    Returns:
    - float: The calculated percentile value.

    Example:
    - percentile([1, 2, 3, 4, 5], 50)  # Returns the median value.
    - percentile([1, 2, 3, 4, 5], 25)  # Returns the 25th percentile.
    """
    sort: list[int] | list[float] = sorted(values)
    index: float = (n / 100) * (len(sort) - 1)
    if index.is_integer():
        return sort[int(index)]
    floor: int = int(index // 1)
    ceiling: int = floor + 1
    fraction: float = index - floor
    return sort[floor] + fraction * (sort[ceiling] - sort[floor])
