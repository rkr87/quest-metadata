"""
github_wrapper.py

This module defines the GitHubWrapper class for fetching external application
information from GitHub.

GitHubWrapper:
    A non-instantiable class with a static method for fetching external
    application information from the specified GitHub URL.

Attributes:
    EXT_APPS (str): The url from which to obtain Github app information.

Usage:
    To use this class, call the static method `get_github_apps()`.

    Example:
    ```python
    from github_wrapper import GitHubWrapper

    # Fetch external applications from GitHub
    apps = GitHubWrapper.get_github_apps()
    ```

Note: Adjust the usage example based on the actual use case in your code.
"""
from logging import Logger, getLogger

from aiohttp import ClientResponse, ClientSession
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.model.github_models import GithubApps

EXT_APPS: str = 'https://raw.githubusercontent.com/basti564' \
    + '/LauncherIcons/main/oculus_apps.json'


@final
class GitHubWrapper(NonInstantiable):
    """
    GitHubWrapper class for fetching external application information
    from GitHub.

    Attributes:
        _launch_method (str): The method to be used for creating instances.
    """

    _launch_method = "get_github_apps"

    @staticmethod
    async def get_github_apps(http_session: ClientSession) -> GithubApps:
        """
        Fetches the list of external applications from the specified URL.

        Returns:
            GithubApps:
                A Pydantic model representing a list of external
                applications retrieved from the GitHub API.
        """
        logger: Logger = getLogger(__name__)
        logger.info("Fetching app update list from Github")
        headers: dict[str, str] = {'Accept': 'application/json'}

        resp: ClientResponse = await http_session.get(
            EXT_APPS,
            headers=headers
        )

        text = await resp.json(content_type='text/plain; charset=utf-8')
        data: GithubApps = GithubApps.model_validate(text)
        return data
