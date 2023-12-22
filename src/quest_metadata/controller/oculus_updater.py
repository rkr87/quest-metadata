"""
Module providing a class for updating Oculus apps.

Classes:
- OculusUpdater: Class for updating Oculus apps.
"""
import asyncio
from logging import Logger, getLogger

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.app_manager import AppManager
from data.model.oculus_models import OculusApp, OculusApps
from data.web.oculus_wrapper import OculusWrapper
from utils.list_utils import flatten_list


@final
class OculusUpdater(NonInstantiable):
    """
    Class for updating Oculus apps.

    Attributes:
    - _launch_method (str): The launch method used for updating.
    """
    _launch_method: str = "update"

    @staticmethod
    async def update(
        app_manager: AppManager,
        wrapper: OculusWrapper
    ) -> None:
        """
        Updates Oculus apps by fetching app information from
        OculusDB and GraphQL.

        Parameters:
        - app_manager (AppManager): An instance of the AppManager for
            managing local app data.
        - wrapper (OculusWrapper): An instance of the OculusWrapper for
            interacting with OculusDB and GraphQL.

        Returns:
        - None
        """
        logger: Logger = getLogger(__name__)

        async def process_app(item: OculusApp) -> list[OculusApp]:
            """
            Asynchronously processes a single Oculus app by fetching version
            and package information, returns a list of OculusApps for each
            unique package name found.

            Parameters:
            - item (OculusApp): The Oculus app to be processed.

            Returns:
            - list[OculusApp]: A list containing the processed Oculus apps.
            """
            if (version := await wrapper.get_version(item.id)) is not None:
                pkg: str | None = await wrapper.get_package(item.id, version)
                return OculusUpdater._update_package(pkg, item)
            return [item]

        apps: OculusApps = await wrapper.get_oculus_apps()
        logger.info("Fetching updates from Oculus")

        results: list[list[OculusApp]] = await asyncio.gather(
            *[process_app(item) for item in apps]
        )
        apps = OculusApps.model_validate(flatten_list(results))

        for app in apps:
            if app.package_name is not None:
                app_manager.add(app.id, app.package_name, app.app_name)
        await app_manager.save()

    @staticmethod
    def _update_package(
        package: str | None,
        item: OculusApp
    ) -> list[OculusApp]:
        """
        Updates the package information for an Oculus app.

        Parameters:
        - package (str | None): The new package name for the app.
        - item (OculusApp): The Oculus app to be updated.

        Returns:
        - list[OculusApp]: A list containing the updated Oculus app.
        """
        if package is None:
            return [item]
        if item.package_name is None:
            item.package_name = package
            return [item]
        if package != item.package_name:
            return [item, OculusApp(
                    id=item.id,
                    app_name=item.app_name,
                    package_name=package)]
        return [item]
