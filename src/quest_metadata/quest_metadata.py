# pyright: reportMissingTypeArgument=false
"""
quest_metadata.py

This module defines the Application class for managing app data.

Application:
    A class that updates local app data from GitHub and fetches
    additional meta data.
"""
import logging
import logging.config
from datetime import datetime, timedelta
from typing import final

from base.singleton import Singleton
from controller.github_updater import GithubUpdater
from controller.meta_updater import MetaUpdater
from data.local.app_manager import AppManager
from data.web.meta_cookie import MetaCookie
from data.web.meta_wrapper import MetaWrapper


@final
class Application(metaclass=Singleton):
    """
    Application class for managing app data.

    Attributes:
        _app_manager (AppManager): The local app manager.
        _meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
    """

    def __init__(
        self,
        app_manager: AppManager,
        meta_wrapper: MetaWrapper
    ) -> None:
        """
        Initialize the Application.

        Args:
            app_manager (AppManager): The local app manager.
            meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.
        """
        self._app_manager: AppManager = app_manager
        self._meta_wrapper: MetaWrapper = meta_wrapper

    def run(self) -> None:
        """
        Run the application.

        This method updates local app data from GitHub and fetches
        additional meta data.
        """
        logger = logging.getLogger(__name__)
        start: datetime = datetime.now()
        GithubUpdater.update(self._app_manager)
        MetaUpdater.start(self._app_manager, self._meta_wrapper)
        delta: timedelta = datetime.now() - start
        logger.info("Completed in %s seconds", delta.seconds)


def main() -> None:
    """
    Initialise dependencies and start the application.
    """
    manager = AppManager()
    cookie: str = MetaCookie.fetch()
    wrapper = MetaWrapper(cookie)
    app = Application(manager, wrapper)
    app.run()


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    main()
