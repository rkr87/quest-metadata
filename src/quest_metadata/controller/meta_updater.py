"""
meta_updater.py

This module defines the Processor class for processing app data.

Processor:
    A class with a static method for fetching and processing app
    data using an AppManager and a MetaWrapper.

Attributes:
    FILES (str): The file path to save processed apps.
"""
from logging import Logger, getLogger

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.app_manager import AppManager
from data.model.local_apps import LocalApps
from data.model.meta_response import MetaResponse
from data.web.meta_wrapper import MetaWrapper

FILES: str = "./data/packages/"


@final
class MetaUpdater(NonInstantiable):
    """
    Processor class for processing app data.

    Attributes:
        _launch_method (str): The launch method for creating instances.
    """
    _launch_method: str = "start"

    @staticmethod
    def start(app_manager: AppManager, meta_wrapper: MetaWrapper) -> None:
        """
        Start processing app data.

        Args:
            app_manager (AppManager): The local app manager.
            meta_wrapper (MetaWrapper): The MetaWrapper for fetching meta data.

        Returns:
            None
        """
        logger: Logger = getLogger(__name__)
        scrape_apps: LocalApps = app_manager.get(True)
        logger.info(
            "Start fetching app metadata from meta (%s to fetch)",
            len(scrape_apps)
        )

        for package, app in scrape_apps.items():
            logger.info("Fetching: %s", app.app_name)
            responses: list[MetaResponse]
            responses = [meta_wrapper.get(id) for id in app.store_ids]
            responses[0].save_json(f"{FILES}{package}.json")
            app_manager.update(package)
            scrape_apps.pop(package)
