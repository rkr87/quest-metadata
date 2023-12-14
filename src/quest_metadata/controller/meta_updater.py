"""
meta_updater.py

This module defines a utility class, MetaUpdater,
for updating meta information for local apps.

It uses a MetaWrapper to fetch meta information for each
app and updates the local app manager accordingly.
"""
import asyncio
from collections.abc import Coroutine
from logging import Logger, getLogger
from typing import Any

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from controller.meta_parser import MetaParser
from data.local.app_manager import AppManager
from data.model.local_apps import LocalApp, LocalApps
from data.model.meta_response import MetaResponse
from data.web.meta_wrapper import MetaWrapper

FILES: str = "./data/packages/"


@final
class MetaUpdater(NonInstantiable):
    """
    Utility class for updating meta information for local apps.

    This class provides a method 'start' to fetch meta information for each app
    from MetaWrapper and update the local app manager.
    """
    _launch_method: str = "start"

    @staticmethod
    async def start(
        app_manager: AppManager,
        meta_wrapper: MetaWrapper
    ) -> None:
        """
        Fetches meta information for each local app and updates the app
        manager.

        Args:
            app_manager (AppManager): The local app manager.
            meta_wrapper (MetaWrapper): The MetaWrapper instance for
                fetching meta information.
        """
        logger: Logger = getLogger(__name__)
        local_apps: LocalApps = app_manager.get()
        logger.info("Fetching %s apps from meta.com", len(local_apps))

        async def scrape(package: str, app: LocalApp) -> None:
            responses: list[MetaResponse] = await meta_wrapper.get(
                app.store_ids
            )
            logger.debug("Fetching: %s", app.app_name)
            if len(responses) > 0:
                result: MetaResponse = MetaParser.parse(responses, package)
                await result.save_json(f"{FILES}{package}.json")
                await app_manager.update(
                    package,
                    result.data.is_available,
                    result.data.is_free
                )
                local_apps.pop(package)
            else:
                logger.info("No responses for %s", package)

        tasks: list[Coroutine[Any, Any, None]] = []
        for package, app in local_apps.items():
            tasks.append(scrape(package, app))
        await asyncio.gather(*tasks)
