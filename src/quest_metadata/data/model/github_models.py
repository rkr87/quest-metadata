"""
github_models.py

This module defines Pydantic models for representing
external applications from GitHub.

GithubApp:
    Pydantic model representing an external application from GitHub.

GithubApps:
    Pydantic model representing a list of external applications from GitHub.

Usage:
    To use these models, create instances of `GithubApp` and `GithubApps`
    as needed.

    Example:
    ```python
    from github_models import GithubApp, GithubApps

    # Create an instance of GithubApp
    app = GithubApp(
        id="123",
        app_name="Sample App",
        package_name="com.sample.app"
    )

    # Create an instance of GithubApps
    apps_list = GithubApps(root=[app])
    ```

Note: Adjust the usage example based on the actual use case and
instantiation of these models in your code.
"""
from typing import Callable

from pydantic import BaseModel

from base.root_list_model import RootListModel
from utils.string_utils import to_camel


class _GithubApp(BaseModel):
    """
    Pydantic model representing an external application from GitHub.

    Attributes:
        id (str): The ID of the application.
        app_name (str): The name of the application.
        package_name (str): The package name of the application.

    Config:
        alias_generator (Callable[..., str]): The alias generator for
            attribute names.
    """
    id: str
    app_name: str
    package_name: str

    class Config:
        """
        Pydantic model configuration.

        Attributes:
            alias_generator (Callable[..., str]): The alias generator for
                attribute names.
        """
        alias_generator: Callable[..., str] = to_camel


class GithubApps(RootListModel[_GithubApp]):  # pylint: disable=too-few-public-methods
    """
    Pydantic model representing a list of external applications from GitHub.
    """
