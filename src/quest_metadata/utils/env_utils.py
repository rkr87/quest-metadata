"""
env_utils.py

This module provides utilities for working with various environments.

Functions:
- github_actions() -> bool: ...
- github_actions(path: str) -> str: ...
"""
import os
from typing import overload


@overload
def github_actions() -> bool:
    """
    Check if the code is running in a GitHub Actions environment.

    Returns:
        bool: True if running in a GitHub Actions environment,
            False otherwise.
    """


@overload
def github_actions(path: str) -> str:
    """
    Construct a path for GitHub Actions or return a local path
    if not running on GitHub Actions.

    Args:
        path (str): The path to be constructed or adjusted.

    Returns:
        str: The constructed or adjusted path.
    """


def github_actions(path: str | None = None) -> bool | str:
    """
    Check if the code is running in a GitHub Actions environment.
    If a path is provided, construct or adjust the path based
    on the environment.

    Args:
        path (str, optional): The path to be constructed or adjusted.

    Returns:
        bool or str: True if running in a GitHub Actions environment,
                    the constructed or adjusted path otherwise.
    """
    on_github: bool = (
        os.environ.get("CI") is not None and
        os.environ.get("GITHUB_RUN_ID") is not None
    )
    if path:
        if on_github:
            return path
        return f".{path}"
    return on_github
