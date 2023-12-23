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
from data.model.meta_response import Item, MetaResponse
from data.web.meta_wrapper import MetaWrapper
from utils.math_utils import percentile


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

        async def scrape(package: str, app: LocalApp) -> MetaResponse | None:
            responses: list[MetaResponse] = \
                await meta_wrapper.get(app.store_ids)

            logger.debug("Fetching: %s", app.app_name)

            if len(responses) == 0:
                logger.info("No responses for %s", package)
                return None

            result: MetaResponse = MetaParser.parse(
                responses,
                package,
                app
            )
            await meta_wrapper.get_resources(result.data.resources)
            await app_manager.update(
                package,
                result.data.is_available,
                result.data.is_free,
                result.data.is_demo_of is not None
            )

            return result

        tasks: list[MetaResponse | None] = \
            await asyncio.gather(*[scrape(p, a) for p, a in apps.items()])

        await app_manager.save()

        votes: list[int] = [i.data.votes for i in tasks if i]
        Item.global_rating = sum(
            i.data.rating * i.data.votes
            for i in tasks if i
        )
        Item.global_votes = sum(votes)
        Item.lower_quartile_votes = percentile(votes, 25)

        await asyncio.gather(
            *[r.save_json(f"{DATA}{r.package}.json") for r in tasks if r]
        )
