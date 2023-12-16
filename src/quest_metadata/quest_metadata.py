"""
quest_metadata.py
This module defines the Application class for managing app data.

Application:
    A class that updates local app data from GitHub and fetches
    additional meta data.

Attributes:
    _app_manager (AppManager): The local app manager.
    _meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
    _github_wrapper (GitHubWrapper): The GitHubWrapper for updating local
        app data.
"""

import asyncio
import logging.config
from datetime import datetime, timedelta
from typing import final

from base.base_class import BaseClass
from base.singleton import Singleton
from controller.github_updater import GithubUpdater
from controller.meta_updater import MetaUpdater
from data.local.app_manager import AppManager
from data.web.github_wrapper import GitHubWrapper
from data.web.http_client import HttpClient
from data.web.meta_cookie import MetaCookie
from data.web.meta_wrapper import MetaWrapper


@final
class Application(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    Application class for managing app data.

    Attributes:
        _app_manager (AppManager): The local app manager.
        _meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
        _github_wrapper (GitHubWrapper): The GitHubWrapper for updating local
            appdata.
    """

    def __init__(
        self,
        app_manager: AppManager,
        meta_wrapper: MetaWrapper,
        github_wrapper: GitHubWrapper
    ) -> None:
        """
        Initialize the Application.

        Args:
            app_manager (AppManager): The local app manager.
            meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
            github_wrapper (GitHubWrapper): The GitHubWrapper for updating
            local app data.
        """
        super().__init__()
        self._app_manager: AppManager = app_manager
        self._meta_wrapper: MetaWrapper = meta_wrapper
        self._github_wrapper: GitHubWrapper = github_wrapper

    async def run(self) -> None:
        """
        Run the application.

        This method updates local app data from GitHub and fetches
        additional meta data.
        """
        start: datetime = datetime.now()
        await GithubUpdater.update(self._app_manager, self._github_wrapper)
        await MetaUpdater.start(self._app_manager, self._meta_wrapper)
        delta: timedelta = datetime.now() - start
        self._logger.info("Completed in %s seconds", delta.seconds)


async def main() -> None:
    """
    Initialise dependencies and start the application.
    """
    manager = AppManager()
    client = HttpClient()
    await client.open_session()
    cookie: str = await MetaCookie.fetch()
    meta_wrapper = MetaWrapper(cookie, client)
    github_wrapper = GitHubWrapper(client)
    app = Application(manager, meta_wrapper, github_wrapper)
    await app.run()


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    asyncio.run(main())
