"""
string_utils.py

This module provides utility functions for string manipulations
and conversions.

Functions:
    - to_snake(string: str) -> str: Convert a string to snake_case.
    - to_pascal(snake: str) -> str: Convert a snake_case string to PascalCase.
    - to_camel(snake: str) -> str: Convert a snake_case string to camelCase.
    - to_kebab(snake: str) -> str: Convert a snake_case string to kebab-case.
    - to_iso(data_str: str, _format: str) -> str: Convert a date string
        to ISO format.

Usage:
    To use these functions, import the module and call the desired
    function as follows:

    ```python
    from string_utils import to_snake, to_pascal, to_camel, to_kebab, to_iso

    snake_case_string = to_snake("MyString")
    pascal_case_string = to_pascal("my_string")
    camel_case_string = to_camel("my_string")
    kebab_case_string = to_kebab("my_string")
    iso_date_string = to_iso("2022-01-01", "%Y-%m-%d")
    ```
"""
from datetime import datetime
from re import sub


def to_snake(string: str) -> str:
    '''
    Convert a string to snake_case.

    Args:
        string (str): The input string.

    Returns:
        str: The string converted to snake_case.
    '''
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                string.replace('-', ' '))).split()).lower()


def to_pascal(snake: str) -> str:
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake (str): The input snake_case string.

    Returns:
        str: The string converted to PascalCase.
    """
    return "".join(x.capitalize() for x in snake.lower().split("_"))


def to_camel(snake: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        snake (str): The input snake_case string.

    Returns:
        str: The string converted to camelCase.
    """
    return snake[0].lower() + to_pascal(snake)[1:]


def to_kebab(snake: str) -> str:
    """
    Convert a snake_case string to kebab-case.

    Args:
        snake (str): The input snake_case string.

    Returns:
        str: The string converted to kebab-case.
    """
    return '-'.join(word for word in snake.split('_'))


def to_iso(data_str: str, _format: str) -> str:
    '''
    Convert a date string to ISO format.

    Args:
        data_str (str): The input date string.
        _format (str): The format of the input date string.

    Returns:
        str: The string converted to ISO format or the original
            string if the conversion fails.
    '''
    try:
        return datetime.strptime(data_str, _format).isoformat()
    except ValueError:
        return data_str
