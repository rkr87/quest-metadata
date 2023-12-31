"""
Module providing utility functions for working with dictionaries.

Functions:
- get_nested_keys: Function to get nested values from a dictionary
    using a key path.
- get_first_existing_key: Function to get the value of the first
    existing key in a list.

"""
from collections.abc import Sequence
from typing import Any

from utils.indexable import safe_get


def get_nested_keys(
    dictionary: dict[str, Any],
    key_path: Sequence[str | int | list[str]]
) -> Any:
    """
    Get nested values from a dictionary using a key path.

    Args:
    - dictionary (dict[str, Any]): The dictionary to extract values from.
    - key_path (Sequence[str | int | list[str]]): The key path to traverse.

    Returns:
    - Any: The value found at the specified key path, or None if not found.

    Details:
    The `get_nested_keys` function allows traversal through a nested dictionary
    using a key path, which can include keys, indices, and lists of keys. If a
    list of keys is encountered, the function will attempt to traverse down
    each branch, returning the first non-None value found. This branching
    behavior allows handling various nested structures within the dictionary.

    Example:
    - dictionary = {'a': {'b': {'d': 42, 'e': 99}}}
    - key_path = ['a', 'b', ['c', 'd', 'e']]
    - result = get_nested_keys(dictionary, key_path)

    In this example, the function will first follow the 'a' key, then 'b' key,
    and finally, it will branch into two paths: one following 'c' and another
    following 'd'. Since 'd' is found in the dictionary, the value 42 will be
    returned.
    """
    value: Any = dictionary
    for item in key_path:
        if not isinstance(item, list):
            value = safe_get(value, item)
            continue
        for trunk in item:
            new_path: list[str | int | list[str]] = [trunk]
            new_path.extend(key_path[key_path.index(item) + 1:])
            if (new_value := get_nested_keys(value, new_path)) is not None:
                return new_value
        return None
    return value


def get_first_existing_key(
    dictionary: dict[str, Any],
    key_list: list[str]
) -> Any:
    """
    Get the value of the first existing key in a list.

    Args:
    - dictionary (dict[str, Any]): The dictionary to search for keys.
    - key_list (list[str]): The list of keys to check.

    Returns:
    - Any: The value of the first existing key, or None if none of the
        keys are found.
    """
    value = None
    for item in key_list:
        if (value := dictionary.get(item)) is not None:
            return value
    return value
