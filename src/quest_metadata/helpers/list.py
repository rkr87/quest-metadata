"""
Module providing utility functions for working with lists.

Functions:
- flatten_list: Function to flatten a list of lists, with an option to exclude
    duplicates.
- safe_list_get: Function to safely get a value from a list by index, with an
    optional default value.

"""
from typing import TypeVar

_T = TypeVar("_T")


def flatten_list(
    list_of_lists: list[list[_T]],
    exclude_duplicates: bool = False
) -> list[_T]:
    """
    Flatten a list of lists, optionally excluding duplicates.

    Args:
    - list_of_lists (list[list[_T]]): The list of lists to flatten.
    - exclude_duplicates (bool, optional): If True, exclude duplicate values in
        the flattened list.

    Returns:
    - list[_T]: The flattened list.

    Example:
    ``` python
    my_list = [[1, 2], [2, 3, 4], [4, 5]]
    flatten_list(my_list) > [1, 2, 2, 3, 4, 4, 5]
    flatten_list(my_list, True) > [1, 2, 3, 4, 5]
    ```
    """
    flattened: list[_T] = []
    for item in list_of_lists:
        if not exclude_duplicates:
            flattened += item
        else:
            flattened += [i for i in item if i not in flattened]
    return flattened


def safe_list_get(
    _list: list[_T],
    index: int,
    default: _T | None = None
) -> _T | None:
    """
    Safely get a value from a list by index, with an optional default value.

    Args:
    - _list (list[_T]): The list to extract the value from.
    - index (int): The index to use for extraction.
    - default (_T | None, optional): The default value to return if the index
        is not found.

    Returns:
    - _T | None: The value found at the specified index, or the default value
        if not found.

    Example:
    ``` python
    my_list = [[1, 2], [2, 3, 4], [4, 5]]
    safe_list_get(my_list, 1) > 2
    safe_list_get(my_list, 5) > None
    safe_list_get(my_list, 5, 0) > 0
    ```
    """
    try:
        return _list[index]
    except IndexError:
        return default
