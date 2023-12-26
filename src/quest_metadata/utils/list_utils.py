"""
Module providing functions for modifying lists.

Functions:
- flatten_list: Flattens a list of lists into a single list.
"""
from typing_extensions import TypeVar

_KT = TypeVar("_KT")


def flatten_list(list_of_lists: list[list[_KT]]) -> list[_KT]:
    """
    Flattens a list of lists into a single list.

    Parameters:
    - list_of_lists (list[list[_KT]]): The list of lists to be flattened.

    Returns:
    - list[_KT]: The flattened list.
    """
    flattened: list[_KT] = []
    for item in list_of_lists:
        flattened += item
    return flattened
