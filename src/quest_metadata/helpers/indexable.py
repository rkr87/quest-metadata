"""
Module providing utility functions for safely getting values from indexable
objects.

Functions:
- safe_get: Function to safely get values from dictionaries or lists with
    optional default values.
"""
from typing import Any, TypeVar, overload

from helpers.list import safe_list_get

_VT = TypeVar("_VT")
_KT = TypeVar("_KT")


@overload
def safe_get(
    indexable: dict[_KT, _VT],
    item: _KT,
    default: _VT | None = None
) -> _VT | None:
    ...


@overload
def safe_get(
    indexable: list[_VT],
    item: int,
    default: _VT | None = None
) -> _VT | None:
    ...


def safe_get(
    indexable: dict[Any, _VT] | list[_VT],
    item: Any,
    default: _VT | None = None
) -> _VT | None:
    """
    Safely get values from dictionaries or lists with optional default values.

    Args:
    - indexable (dict[Any, _VT] | list[_VT]): The dictionary or list to extract
        values from.
    - item (Any): The key or index to use for extraction.
    - default (_VT | None, optional): The default value to return if the key or
        index is not found.

    Returns:
    - _VT | None: The value found at the specified key or index, or the default
        value if not found.

    Details:
    The `safe_get` function is designed to safely extract values from
    dictionaries or lists, returning the specified default value if the key or
    index is not found. It also checks the type of the indexable object and
    redirects the call to `safe_list_get` for lists.
    """
    if isinstance(indexable, list) and isinstance(item, int):
        return safe_list_get(indexable, item, default)
    if isinstance(indexable, dict):
        return indexable.get(item, default)
    return None
