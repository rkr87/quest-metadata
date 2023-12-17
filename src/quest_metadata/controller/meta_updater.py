"""
meta_updater.py

This module defines a utility class, MetaUpdater,
for updating meta information for local apps.

It uses a MetaWrapper to fetch meta information for each
app and updates the local app manager accordingly.
"""
import asyncio
from logging import Logger, getLogger

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from constants.constants import DATA
from controller.meta_parser import MetaParser
from data.local.app_manager import AppManager
from data.model.local_apps import LocalApp, LocalApps
from data.model.meta_response import MetaResponse
from data.web.meta_wrapper import MetaWrapper


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
        apps: LocalApps = app_manager.get()
        logger.info("Fetching %s apps from meta.com", len(apps))

        async def scrape(package: str, app: LocalApp) -> None:
            responses: list[MetaResponse] = await meta_wrapper.get(
                app.store_ids
            )
            logger.debug("Fetching: %s", app.app_name)
            if len(responses) > 0:
                result: MetaResponse = MetaParser.parse(responses, package)
                if app.logos is not None:
                    result.data.logo_landscape = app.logos.landscape
                    result.data.logo_portrait = app.logos.portrait
                await result.save_json(f"{DATA}{package}.json")
                await meta_wrapper.get_resources(result.data.resources)
                await app_manager.update(
                    package,
                    result.data.is_available,
                    result.data.is_free
                )
            else:
                logger.info("No responses for %s", package)

        await asyncio.gather(*[scrape(pkg, app) for pkg, app in apps.items()])
