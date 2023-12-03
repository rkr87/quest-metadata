"""
processor.py

This module defines the Processor class for processing app data.

Processor:
    A class with a static method for fetching and processing app
    data using an AppManager and a MetaWrapper.

Attributes:
    FILES (str): The file path to save processed apps.
"""
import logging

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.app_manager import AppManager
from data.model.local_apps import LocalApps
from data.model.meta_models import MetaResponse
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
        logger = logging.getLogger(__name__)
        scrape_apps: LocalApps = app_manager.get(True)
        logger.info(
            "Start fetching app metadata from meta (%s to fetch)",
            len(scrape_apps)
        )

        for key, local_app in scrape_apps.items():
            logger.info("Fetching: %s", local_app.app_name)
            response: MetaResponse = meta_wrapper.get(key)
            json_text: str = response.model_dump_json(
                indent=4,
                exclude_unset=True,
                exclude_none=True
            )
            for package in local_app.packages:
                with open(
                    f"{FILES}{package}.json", 'w', encoding="utf-8"
                ) as file:
                    file.write(json_text)
            app_manager.update(key)
            scrape_apps.pop(key)
