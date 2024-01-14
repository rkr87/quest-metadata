"""
Module providing utility functions for string transformations.

Functions:
- to_snake: Convert a string to snake_case.
- to_pascal: Convert a string to PascalCase.
- to_camel: Convert a string to camelCase.
- to_kebab: Convert a string to kebab-case.
- to_iso: Convert a date string to ISO format.

"""
import re
from datetime import datetime
from re import sub


def to_snake(string: str) -> str:
    """
    Convert a string to snake_case.

    Args:
    - string (str): The input string.

    Returns:
    - str: The converted string in snake_case.

    Example:
    ``` python
    to_snake("CamelCaseString") > "camel_case_string"
    ```
    """
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                string.replace('-', ' '))).split()).lower()


def to_pascal(snake: str) -> str:
    """
    Convert a string to PascalCase.

    Args:
    - snake (str): The input string in snake_case.

    Returns:
    - str: The converted string in PascalCase.

    Example:
    ``` python
    to_pascal("snake_case_string") > "SnakeCaseString"
    ```
    """
    return "".join(x.capitalize() for x in snake.lower().split("_"))


def to_camel(snake: str) -> str:
    """
    Convert a string to camelCase.

    Args:
    - snake (str): The input string in snake_case.

    Returns:
    - str: The converted string in camelCase.

    Example:
    ```python
    to_camel("snake_case_string") > "snakeCaseString"
    ```
    """
    return snake[0].lower() + to_pascal(snake)[1:]


def to_kebab(snake: str) -> str:
    """
    Convert a string to kebab-case.

    Args:
    - snake (str): The input string in snake_case.

    Returns:
    - str: The converted string in kebab-case.

    Example:
    ```python
    to_kebab("snake_case_string") > "snake-case-string"
    ```
    """
    return '-'.join(word for word in snake.split('_'))


def to_iso(date_str: str, input_format: str) -> str:
    """
    Convert a date string to ISO format.

    Args:
    - date_str (str): The input date string.
    - input_format (str): The format of the input date string.

    Returns:
    - str: The converted date string in ISO format, or the original
        string if conversion fails.

    Example:
    ```python
    to_iso("2022-01-01", "%Y-%m-%d") > "2022-01-01T00:00:00".
    ```
    """
    try:
        return datetime.strptime(date_str, input_format).isoformat()
    except ValueError:
        return date_str


def normalise_text(text: str, strip_words: list[str] | None = None) -> str:
    """
    Normalize text by removing non-alphanumeric characters and converting to
    lowercase.

    Args:
    - text (str): The input text.
    - strip_words (list[str] | None): List of words to strip from the text.

    Returns:
    - str: The normalized text.

    Example:
    ```python
    normalise_text("Hello World! 123") > "hello world 123"
    ```
    """
    pattern = "[^a-z0-9\\s]"
    clean: str = re.sub(pattern, "", text.lower())

    if strip_words is None:
        return clean

    noise: list[str] = [normalise_text(x) for x in strip_words]

    return " ".join([x for x in clean.split(" ") if x not in noise])


def normalised_compare(
    text_a: str,
    text_b: str,
    strip_words: list[str] | None = None
) -> bool:
    """
    Compare two normalized texts.

    Args:
    - text_a (str): The first text.
    - text_b (str): The second text.
    - strip_words (list[str] | None): List of words to strip from the text.

    Returns:
    - bool: True if the normalized texts are equal, False otherwise.

    Example:
    ```python
    normalised_compare("Hello TEST World! 1", "HELLO world 1", ["Test"]) > True
    ```
    """
    compare_a: str = normalise_text(text_a, strip_words)
    compare_b: str = normalise_text(text_b, strip_words)
    return compare_a == compare_b
