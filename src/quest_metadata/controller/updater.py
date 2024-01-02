"""
Module providing the Updater class for updating and scraping Oculus apps.

Classes:
- Updater: Singleton class for updating and scraping Oculus apps.
"""
import asyncio

from aiofiles import open as aopen
from aiofiles.os import makedirs, path, remove
from typing_extensions import final

from base.classes import Singleton
from base.lists import LowerCaseUniqueList
from config.app_config import AppConfig
from controller.image_manager import ImageManager
from controller.parser import Parser
from data.local.app_manager import AppManager
from data.model.local.apps import LocalApp, LocalApps
from data.model.oculus.app import Item, OculusApp
from data.model.oculus.app_additionals import AppAdditionalDetails, AppImage
from data.model.oculus.app_package import AppPackage
from data.model.oculus.app_versions import AppVersions
# from data.model.oculus.store_section import StoreSection
from data.model.oculusdb.apps import OculusDbApps
from data.model.parsed.app_item import ParsedAppItem
from data.web.wrapper import Wrapper
from utils.math import percentile


@final
class Updater(Singleton):
    """
    Singleton class for updating and scraping Oculus apps.

    Attributes:
    - _app_manager (AppManager): Instance of AppManager for managing local
        apps.
    - _wrapper (Wrapper): Instance of Wrapper for making web requests.
    - _image_manager (ImageManager): Instance of ImageManager for resizing and
        cropping images.
    """

    def __init__(
        self,
        app_manager: AppManager,
        wrapper: Wrapper,
        image_manager: ImageManager
    ) -> None:
        super().__init__()
        self._logger.info("Initializing updater")
        self._app_manager: AppManager = app_manager
        self._wrapper: Wrapper = wrapper
        self._image_manager: ImageManager = image_manager

    async def update_local_apps(self) -> None:
        """
        Update local apps by collecting package names and parsing data.
        """
        oculusdb: OculusDbApps = await self._wrapper.get_oculusdb_apps()
        self._logger.info("Collecting package names for each OculusDB app")

        parsed: list[ParsedAppItem] = await asyncio.gather(*[
            self._parse_result(i.id, i.app_name, i.package_name)
            for x, i in enumerate(oculusdb) if x < 2000  # pylint: disable=R2004
        ])

        # parsed_ids: list[str] = [i.id for i in parsed]

        # oculus: StoreSection = await self._wrapper.get_store_apps()
        # parsed += await asyncio.gather(*[
        #     self._parse_result(i.id, i.display_name)
        #     for i in oculus
        #     if i.id not in parsed_ids
        # ])

        self._logger.info("Collecting package names for each Oculus app")

        for item in parsed:
            self._app_manager.add(item)
        await self._app_manager.save()

    async def _parse_result(
        self,
        app_id: str,
        app_name: str,
        known_package: str | None = None
    ) -> ParsedAppItem:
        """
        Parse and consolidate data from OculusDB and Oculus.

        Parameters:
        - app_id (str): The ID of the app.
        - app_name (str): The name of the app.
        - known_package (Optional[str]): Known package name.

        Returns:
        ParsedAppItem: Parsed data for the app.
        """
        parsed = ParsedAppItem(id=app_id, name=app_name)
        parsed.versions = await self._wrapper.get_app_versions(app_id)
        if parsed.versions is None:
            return parsed
        parsed.packages = await self._get_version_packages(
            app_id,
            parsed.versions
        )
        parsed.packages.append(known_package)
        return parsed

    async def _get_version_packages(
        self,
        app_id: str,
        versions: AppVersions
    ) -> LowerCaseUniqueList:
        """
        Get packages for a specific app version.

        Parameters:
        - app_id (str): The ID of the app.
        - versions (AppVersions): Versions of the app.

        Returns:
        LowerCaseUniqueList: List of unique lowercase package names.
        """
        packages: LowerCaseUniqueList = LowerCaseUniqueList()
        for version in versions:
            pkg: AppPackage | None = await self._wrapper.get_version_package(
                app_id,
                version.code
            )
            if pkg is not None:
                packages.append(pkg.name)
        return packages

    async def scrape_apps(self) -> None:
        """
        Scrape apps from oculus.com, update local apps, and calculate average
        ratings.
        """
        apps: LocalApps = self._app_manager.get()
        self._logger.info("Fetching %s apps from oculus.com", len(apps))

        tasks: list[OculusApp | None] = await asyncio.gather(
            *[self._scrape_app(p, a) for p, a in apps.items()]
        )

        await self._app_manager.save()

        self._calc_average_ratings([i for i in tasks if i])
        await asyncio.gather(*[
            r.save_json(f"{AppConfig().data_path}/{r.package}.json")
            for r in tasks if r
        ])

    @staticmethod
    def _calc_average_ratings(items: list[OculusApp]) -> None:
        """
        Calculate average ratings based on scraped data.

        Parameters:
        - items (List[OculusApp]): List of scraped OculusApp instances.
        """
        votes: list[int] = [i.data.votes for i in items]
        ratings: list[float] = [i.data.rating for i in items]
        mean: float = sum(a * b for a, b in zip(votes, ratings)) / sum(votes)
        median: float = percentile(ratings, 50)
        Item.global_average_rating = min(median, mean)
        Item.vote_confidence = percentile(votes, 25)

    async def _scrape_app(
        self,
        package: str,
        app: LocalApp
    ) -> OculusApp | None:
        """
        Scrape details, additional IDs, and images for a specific app.

        Parameters:
        - package (str): The package name of the app.
        - app (LocalApp): LocalApp instance representing the app.

        Returns:
        Optional[OculusApp]: The scraped OculusApp instance or None if no
            response.
        """
        if (primary := await self._scrape_app_id(app.id)) is None:
            self._logger.info(
                "No response for %s (%s) [%s]",
                app.app_name,
                package,
                app.id
            )
            return None

        additional: list[OculusApp] = \
            await self._get_additional_ids(app.additional_ids)
        result: OculusApp = Parser.parse(primary, additional, package)

        image_downloads: list[AppImage] = \
            await self._wrapper.get_resources(result.data.resources)
        await self._process_images(image_downloads)
        await self._app_manager.update(
            package,
            result.data.is_available,
            result.data.is_free,
            result.data.is_demo_of is not None
        )
        return result

    async def _get_additional_ids(
        self,
        id_list: list[str] | None
    ) -> list[OculusApp]:
        """
        Get additional OculusApp instances for a list of IDs.

        Parameters:
        - id_list (List[str] | None): List of app IDs or None.

        Returns:
        List[OculusApp]: List of additional OculusApp instances.
        """
        if id_list is None:
            return []
        additional: list[OculusApp | None] = await asyncio.gather(
            *[self._scrape_app_id(i) for i in id_list]
        )
        return [a for a in additional if a is not None]

    async def _scrape_app_id(self, app_id: str) -> OculusApp | None:
        """
        Scrape app details and additional details for a specific app ID.

        Parameters:
        - app_id (str): The ID of the app.

        Returns:
        Optional[OculusApp]: The scraped OculusApp instance or None if no
            response.
        """
        if (app := await self._wrapper.get_app_details(app_id)) is None:
            return None
        additionals: AppAdditionalDetails | None = \
            await self._wrapper.get_app_additionals(app_id)
        if additionals is not None:
            app.data.set_additional_details(additionals)
        return app

    async def _process_images(self, images: list[AppImage]) -> None:
        """
        Process and save images for a list of AppImage instances.

        Parameters:
        - images (List[AppImage]): List of AppImage instances.
        """
        for image in images:
            if image.data is None:
                continue
            if (directory := await self._check_dir(image)) is None:
                return
            resize: bytes = await self._image_manager.resize_image(
                image.data,
                image.props
            )
            file_path: str = f"{directory}{image.name}"
            await self._save_image(resize, file_path)

    async def _save_image(self, image_data: bytes, file_path: str) -> None:
        """
        Save image data to a file.

        Parameters:
        - image_data (bytes): Image data to be saved.
        - file_path (str): The path where the image will be saved.
        """
        try:
            async with aopen(file_path, 'wb') as file:
                await file.write(image_data)
        except asyncio.TimeoutError:
            self._logger.info(
                "Failed saving file: %s",
                file_path
            )
            if await path.exists(file_path):
                await remove(file_path)
            return None

    async def _check_dir(self, res: AppImage) -> str | None:
        """
        Check and create the directory for saving images.

        Parameters:
        - res (AppImage): AppImage instance representing an image resource.

        Returns:
        Optional[str]: The directory path or None if creating the directory
            fails.
        """
        directory: str = f"{AppConfig().resource_path}/{res.type}/"
        try:
            await makedirs(directory, exist_ok=True)
        except asyncio.TimeoutError:
            self._logger.info("Failed creating directory: %s", directory)
            return None
        return directory
