"""
github_wrapper.py

This module defines a GitHubWrapper class that interacts with GitHub to
fetch app update lists.

GitHubWrapper:
    A class with a method for fetching external application information
    from the specified GitHub URL.

Attributes:
    EXT_APPS (str): The URL from which to obtain GitHub app information.

Usage:
    To use this class, create an instance by passing an HttpClient instance,
    and then call the method `get_github_apps()`.

Example:
    ```python
    from github_wrapper import GitHubWrapper
    from data.web.http_client import HttpClient

    # Create an instance of HttpClient (provide appropriate parameters)
    http_client = HttpClient()

    # Create an instance of GitHubWrapper
    github_wrapper = GitHubWrapper(http_client)

    # Fetch external applications from GitHub
    apps = await github_wrapper.get_github_apps()
    ```
"""
from aiohttp import ClientResponse
from typing_extensions import final

from base.base_class import BaseClass
from base.singleton import Singleton
from data.model.github_models import GithubApps
from data.web.http_client import HttpClient

EXT_APPS: str = (
    'https://raw.githubusercontent.com/basti564/LauncherIcons/main/oculus_apps.json'
)


@final
class GitHubWrapper(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    GitHubWrapper class for fetching external application information
    from GitHub.

    Attributes:
        _client (HttpClient): The HttpClient instance for making HTTP requests.
    """

    def __init__(self, http_client: HttpClient) -> None:
        """
        Initialize the GitHubWrapper instance.

        Args:
            http_client (HttpClient): An instance of the HttpClient class
                used for making HTTP requests.
        """
        super().__init__()
        self._logger.info("Initializing GitHub Wrapper")
        self._client: HttpClient = http_client

    async def get_github_apps(self) -> GithubApps:
        """
        Fetch the list of external applications from the specified URL.

        Returns:
            GithubApps:
                A Pydantic model representing a list of external
                applications retrieved from the GitHub API.
        """
        self._logger.info("Fetching app update list from GitHub")
        headers: dict[str, str] = {'Accept': 'application/json'}

        resp: ClientResponse | None = await self._client.get(
            EXT_APPS,
            headers=headers
        )

        if resp is None:
            return GithubApps()

        text = await resp.json(content_type='text/plain; charset=utf-8')
        data: GithubApps = GithubApps.model_validate(text)
        return data
