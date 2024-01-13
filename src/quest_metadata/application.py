"""
Module providing the Application class for managing and updating Oculus apps.

Classes:
- Application: Singleton class for managing and updating Oculus apps.
"""
from collections.abc import Generator
from datetime import datetime, timedelta
from typing import Any, final

from aiofiles.os import makedirs as amakedirs

from base.classes import Singleton
from config.app_config import AppConfig
from controller.image_manager import ImageManager
from controller.updater import Updater
from data.local.app_manager import AppManager
from data.web.google import GoogleSheetService
from data.web.http_client import HttpClient
from data.web.oculus import OculusService
from data.web.rookie import RookieService
from utils.async_runner import AsyncRunner


@final
class Application(Singleton):
    """Singleton class for managing and updating Oculus apps."""

    def __init__(self) -> None:
        super().__init__()
        self._updater: Updater

    async def _async_init(self) -> "Application":
        """
        Asynchronously initialize the Application instance.

        Returns:
        Application: The initialized Application instance.
        """
        app_manager: AppManager = AppManager()
        async_runner = AsyncRunner(workers=AppConfig().max_threads)
        image_manager = ImageManager(async_runner)
        client = HttpClient()
        await client.open_session()
        oculus = OculusService(client)
        sheets = GoogleSheetService()
        rookie = RookieService()
        self._updater = Updater(
            app_manager,
            oculus,
            image_manager,
            sheets,
            rookie
        )
        await self._setup_environment()
        return self

    def __await__(self) -> Generator[Any, None, "Application"]:
        """
        Coroutine for awaiting asynchronous initialization.

        Returns:
        Generator: A generator to await the asynchronous initialization.
        """
        return self._async_init().__await__()

    @staticmethod
    async def _setup_environment() -> None:
        """
        Set up the environment for the application.
        """
        config = AppConfig()
        await amakedirs(config.data_path, exist_ok=True)
        await amakedirs(config.resource_path, exist_ok=True)

    async def run(self) -> None:
        """
        Run the application, updating local apps and scraping app data.
        """
        start: datetime = datetime.now()
        await self._updater.update_local_apps()
        delta: timedelta = datetime.now() - start
        self._logger.info(
            "Finished updating app list in %s seconds",
            delta.seconds
        )
        start = datetime.now()
        await self._updater.scrape_apps()
        delta = datetime.now() - start
        self._logger.info(
            "Finished scraping app data and resources in %s seconds",
            delta.seconds
        )
