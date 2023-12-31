"""
Module providing utility functions for the current environment.

Functions:
- github_actions: Function to check if the code is running in a
    GitHub Actions environment and retrieve paths accordingly.

"""
import os
from typing import overload


@overload
def github_actions() -> bool: ...


@overload
def github_actions(path: str) -> str: ...


def github_actions(path: str | None = None) -> bool | str:
    """
    Check if the code is running in a GitHub Actions environment and retrieve
    paths accordingly.

    Args:
    - path (str | None, optional): A path to be appended if the code is
        running on GitHub Actions.

    Returns:
    - bool | str: If no path is provided, returns a boolean indicating if the
        code is running on GitHub Actions. If a path is provided, returns the
        path prefixed with a dot ('.') if not on GitHub Actions, or the path
        as-is if on GitHub Actions.

    Example:
    ```python
    # running in local environment
    github_actions() > False
    github_actions("data/") > ".data/"

    # running as github action
    github_actions() > True
    github_actions("data/") > "data/"
    ```
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
