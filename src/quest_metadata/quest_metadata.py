# pyright: reportMissingTypeArgument=false
"""
quest_metadata.py

This module defines the Application class for managing app data.

Application:
    A class that updates local app data from GitHub and fetches
    additional meta data.
"""
import asyncio
import logging.config
from datetime import datetime, timedelta
from typing import final

from aiohttp import ClientSession

from base.base_class import BaseClass
from base.singleton import Singleton
from controller.github_updater import GithubUpdater
from controller.meta_updater import MetaUpdater
from data.local.app_manager import AppManager
from data.web.http_client import HttpClient
from data.web.meta_cookie import MetaCookie
from data.web.meta_wrapper import MetaWrapper


@final
class Application(BaseClass, metaclass=Singleton):
    """
    Application class for managing app data.

    Attributes:
        _app_manager (AppManager): The local app manager.
        _meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
    """

    def __init__(
        self,
        app_manager: AppManager,
        meta_wrapper: MetaWrapper,
        http_session: ClientSession
    ) -> None:
        """
        Initialize the Application.

        Args:
            app_manager (AppManager): The local app manager.
            meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
        """
        super().__init__()
        self._app_manager: AppManager = app_manager
        self._meta_wrapper: MetaWrapper = meta_wrapper
        self._http_session: ClientSession = http_session

    async def run(self) -> None:
        """
        Run the application.

        This method updates local app data from GitHub and fetches
        additional meta data.
        """
        start: datetime = datetime.now()
        await GithubUpdater.update(self._app_manager, self._http_session)
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
    # cookie: str = "locale=en_GB;datr=WjR4ZVGsNzKJQ4FPrNAHpqGf;csrf=tZYcRP_RB3w-1Q_zxCPn6J;gu=ARNVLgsuxcHDAQtZSfjZMRbJvGlzdTnXfAGys7dBitJ7uI_WUsQ-E2cyUUqz9dbd9rT16zJD0EO5MGbyhhXF-w5KqD4umIrRsw6xuKUy6LBq3L84LNy0ID7WBKCR9A4.0"  # pylint: disable=C0301
    wrapper = MetaWrapper(cookie, client())
    app = Application(manager, wrapper, client())
    await app.run()


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    asyncio.run(main())
