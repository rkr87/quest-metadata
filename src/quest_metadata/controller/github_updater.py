"""
github_updater.py

This module defines the GithubUpdater class responsible for updating the
local AppManager with information obtained from the GitHub repository.

GithubUpdater:
    A non-instantiable class with a static method for updating the local
    AppManager with information from the GitHub repository.

Attributes:
    _launch_method (str): The method to be used for creating instances.

Usage:
    To use this class, call the static method `update(app_manager)`.

    Example:
    ```python
    from github_updater import GithubUpdater
    from data.local.app_manager import AppManager

    # Create an instance of the local AppManager
    app_manager = AppManager()

    # Update the AppManager with information from GitHub
    GithubUpdater.update(app_manager)
    ```

Note: Adjust the usage example based on the actual use case in your code.
"""
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.app_manager import AppManager
from data.web.github_wrapper import GitHubWrapper


@final
class GithubUpdater(NonInstantiable):
    """
    GitHub Updater class responsible for updating the local app manager with
    information obtained from the GitHub repository.

    Attributes:
        _launch_method (str): The method to be used for creating instances.
    """
    _launch_method: str = "update"

    @staticmethod
    def update(app_manager: AppManager) -> None:
        """
        Update the provided AppManager with information from the GitHub
        repository.

        Args:
            app_manager (AppManager): The local AppManager to be updated.

        Returns:
            None
        """
        for item in GitHubWrapper.get_github_apps():
            app_manager.add(item.id, item.package_name, item.app_name)
        app_manager.save()
