"""
Module providing the main application class and entry point.

Classes:
- Application: Main application class for orchestrating updates.
"""
import asyncio
import logging.config
import os
from datetime import datetime, timedelta
from typing import final

from base.base_class import BaseClass
from base.singleton import Singleton
from constants.constants import DATA, RESOURCES
from controller.meta_updater import MetaUpdater
from controller.oculus_updater import OculusUpdater
from data.local.app_manager import AppManager
from data.web.http_client import HttpClient
from data.web.meta_cookie import MetaCookie
from data.web.meta_wrapper import MetaWrapper
from data.web.oculus_wrapper import OculusWrapper


@final
class Application(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    Main application class for orchestrating updates.

    Attributes:
    - _app_manager (AppManager): An instance of the AppManager for managing
        local app data.
    - _meta_wrapper (MetaWrapper): An instance of the MetaWrapper for
        interacting with the Meta API.
    - _oculus_wrapper (OculusWrapper): An instance of the OculusWrapper for
        interacting with OculusDB and GraphQL.
    """

    def __init__(
        self,
        app_manager: AppManager,
        meta_wrapper: MetaWrapper,
        oculus_wrapper: OculusWrapper
    ) -> None:
        """
        Initialize the Application instance.

        Parameters:
        - app_manager (AppManager): An instance of the AppManager for managing
            local app data.
        - meta_wrapper (MetaWrapper): An instance of the MetaWrapper for
            interacting with the Meta API.
        - oculus_wrapper (OculusWrapper): An instance of the OculusWrapper for
            interacting with OculusDB and GraphQL.
        """
        super().__init__()
        self._app_manager: AppManager = app_manager
        self._meta_wrapper: MetaWrapper = meta_wrapper
        self._oculus_wrapper: OculusWrapper = oculus_wrapper

    async def run(self) -> None:
        """
        Run the main application process, updating Oculus apps and starting
        Meta updates.
        """
        start: datetime = datetime.now()
        await OculusUpdater.update(self._app_manager, self._oculus_wrapper)
        await MetaUpdater.start(self._app_manager, self._meta_wrapper)
        delta: timedelta = datetime.now() - start
        self._logger.info("Completed in %s seconds", delta.seconds)


async def main() -> None:
    """
    Main entry point for the application.

    Returns:
    - None
    """

    manager = AppManager()

    client = HttpClient()
    await client.open_session()

    oculus_wrapper = OculusWrapper(client)

    cookie: str = await MetaCookie.fetch()
    meta_wrapper: MetaWrapper = await MetaWrapper(cookie, client)

    app = Application(manager, meta_wrapper, oculus_wrapper)
    await app.run()


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(RESOURCES, exist_ok=True)
    asyncio.run(main())
