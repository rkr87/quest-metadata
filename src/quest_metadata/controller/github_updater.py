"""
github_updater.py
This module defines the GithubUpdater class responsible for updating the
local AppManager with information obtained from the GitHub repository.

GithubUpdater:
    A non-instantiable class with a static method for updating the local
    AppManager with information from the GitHub repository.

Attributes:
    _launch_method (str): The method used for creating instances.

Usage:
    To use this class, call the static method `update(...)`.

Example:
    ```python
    from github_updater import GithubUpdater
    from data.web.github_wrapper import GitHubWrapper
    from data.local.app_manager import AppManager

    app_manager = AppManager()
    client = HttpClient()
    await client.open_session()
    github_wrapper = GitHubWrapper(client)

    await GithubUpdater.update(app_manager, github_wrapper)
    ```
"""
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.app_manager import AppManager
from data.model.github_models import GithubApps
from data.web.github_wrapper import GitHubWrapper


@final
class GithubUpdater(NonInstantiable):
    """
    GitHubUpdater class responsible for updating the local AppManager with
    information obtained from the GitHub repository.

    Attributes:
        _launch_method (str): The method used for creating instances.
    """
    _launch_method: str = "update"

    @staticmethod
    async def update(
        app_manager: AppManager,
        github_wrapper: GitHubWrapper
    ) -> None:
        """
        Update the provided AppManager with information from the GitHub
        repository.

        This method fetches information about GitHub apps using the provided
        `github_wrapper` and updates the local `AppManager` with the retrieved
        data. It iterates through the fetched information and adds each item's
        details (such as id, package_name, and app_name) to the AppManager.

        Args:
            app_manager (AppManager): The local AppManager to be updated.
            github_wrapper (GitHubWrapper): The GitHubWrapper for fetching
                update information.
        """
        update: GithubApps = await github_wrapper.get_github_apps()
        for item in update:
            app_manager.add(item.id, item.package_name, item.app_name)
        await app_manager.save()
