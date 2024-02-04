"""
Module providing the Updater class for updating and scraping Oculus apps.

Classes:
- Updater: Singleton class for updating and scraping Oculus apps.
"""
import asyncio
from collections.abc import Coroutine
from typing import Any, final

from aiofiles import open as aopen
from aiofiles.os import makedirs, path, remove

from base.classes import Singleton
from base.lists import LowerCaseUniqueList
from config.app_config import AppConfig
from controller.image_manager import ImageManager
from data.local.app_manager import AppManager
from data.model.applab.apps import AppLabApps
from data.model.local.apps import LocalApp, LocalApps
from data.model.oculus.app import Item, OculusApp
from data.model.oculus.app_additionals import AppAdditionalDetails, AppImage
from data.model.oculus.app_changelog import AppChangeLog
from data.model.oculus.app_package import AppPackage
from data.model.oculus.app_versions import AppVersions
from data.model.oculus.store_search import SearchResult
from data.model.oculus.store_section import StoreSection
from data.model.oculusdb.apps import OculusDbApps
from data.model.parsed.app_item import ParsedAppItem
from data.web.google import GoogleSheetService
from data.web.oculus import OculusService
from data.web.rookie import RookieService
from helpers.math import percentile
from utils.error_manager import ErrorManager


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
        oculus: OculusService,
        image_manager: ImageManager,
        sheet_service: GoogleSheetService,
        rookie_service: RookieService
    ) -> None:
        super().__init__()
        self._logger.info("Initializing updater")
        self._app_manager: AppManager = app_manager
        self._oculus: OculusService = oculus
        self._image_manager: ImageManager = image_manager
        self._sheet_service: GoogleSheetService = sheet_service
        self._rookie: RookieService = rookie_service
        self._parsed_apps: list[ParsedAppItem] = []

    async def update_local_apps(self) -> None:
        """
        Update local apps by collecting package names and parsing data.
        """
        await self._update_oculusdb_apps()
        await self._update_store_apps()
        await self._update_applab_apps()
        await self._update_package_mappings()
        await self._update_local_app_database()
        await self._populate_missing_changelogs()
        self._parse_rookie_updates()
        await self._identify_missing_apps()
        await self._app_manager.save()

    async def _identify_missing_apps(self) -> None:
        """Search the meta store for app names without an identifiable id"""
        async def search(app: LocalApp) -> None:
            if app.id is None:
                search: list[SearchResult] = \
                    await self._oculus.store_search(app.app_name)
                for result in search:
                    if result.id not in self._get_parsed_ids():
                        await self._oculus.oculusdb_report_missing(result.id)
                        self._logger.info("Report: %s", result.display_name)

        apps: LocalApps = self._app_manager.get()
        self._logger.info("Attempting to identify missing apps.")
        await asyncio.gather(*[search(a) for a in apps.values()])

    async def _update_oculusdb_apps(self) -> None:
        """
        Update the list of OculusDB apps, collect package names, and parse
        data.
        """
        oculusdb: OculusDbApps = await self._oculus.get_oculusdb_apps()
        self._logger.info("Collecting package names for each OculusDB app")
        parsed: list[ParsedAppItem] = await asyncio.gather(*[
            self._parse_result(i.id, i.app_name, i.package_name)
            for i in oculusdb
        ])
        self._update_parsed_apps(parsed)

    async def _update_store_apps(self) -> None:
        """
        Update the list of Oculus Store apps, collect package names, and parse
        data.
        """
        oculus: StoreSection = await self._oculus.get_store_apps()
        self._logger.info("Collecting package names for each Oculus app")
        parsed: list[ParsedAppItem] = await asyncio.gather(*[
            self._parse_result(i.id, i.display_name)
            for i in oculus
            if i.id not in self._get_parsed_ids()
        ])
        self._update_parsed_apps(parsed)

    async def _update_applab_apps(self) -> None:
        """
        Update the list of applabgamelist apps, collect package names, and
        parse data.
        """
        applab: AppLabApps = await self._oculus.get_applab_apps()
        self._logger.info("Collecting package names for each applab app")
        parsed: list[ParsedAppItem] = await asyncio.gather(*[
            self._parse_result(i.id, i.app_name)
            for i in applab
            if i.id not in self._get_parsed_ids()
        ])
        self._update_parsed_apps(parsed)

    async def _update_package_mappings(self) -> None:
        """Update package mappings by collecting data from Google Forms."""
        if package_mappings := self._sheet_service.get_package_mappings():
            mapping_tasks: list[Coroutine[Any, Any, ParsedAppItem]] = []
            self._logger.info("Collecting package mappings from Google Forms")
            for i in package_mappings.root:
                if (x := self._get_parsed_ids()) and i.store_id not in x:
                    mapping_tasks.append(
                        self._parse_result(i.store_id, i.name, i.package)
                    )
                    continue
                dupe: ParsedAppItem = self._parsed_apps[x.index(i.store_id)]
                dupe.packages.append(i.package)

            parsed: list[ParsedAppItem] = await asyncio.gather(*mapping_tasks)
            self._update_parsed_apps(parsed)

    async def _update_local_app_database(self) -> None:
        """Update the local app database with parsed app data."""
        self._logger.info("Updating local apps database")
        for item in self._parsed_apps:
            self._app_manager.add(item)

    async def _populate_missing_changelogs(self) -> None:
        """Populate missing changelogs for local apps."""
        self._logger.info("Populating missing changelogs")
        for p, a in self._app_manager.get_needs_changelog().items():
            if a.id and (log := await self._oculus.get_app_changelog(a.id)):
                self._app_manager.add_changelog(p, log)

    def _parse_rookie_updates(self) -> None:
        """Add Rookie releases to local apps."""
        self._logger.info("Adding Rookie releases")
        for package, versions in self._rookie.get_releases().items():
            self._app_manager.add_rookie_releases(package, versions)

    def _update_parsed_apps(self, parsed: list[ParsedAppItem]) -> None:
        """Update the list of parsed apps with new data."""
        self._parsed_apps += parsed

    def _get_parsed_ids(self) -> list[str]:
        """Get a list of IDs from the parsed apps."""
        return [i.id for i in self._parsed_apps if i.id]

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
        if (app := self._app_manager.get_app_by_id(app_id)) is not None:
            updated: bool = False
            log: AppChangeLog | None = \
                await self._oculus.get_app_changelog(app_id)
            if log is not None and len(log) > 0:
                updated = self._app_manager.add_changelog(app[0], log)
                parsed.cl_version = max(i.code for i in log.root)
            if not updated:
                parsed.packages.extend([known_package, app[0]])
                return parsed
        parsed.versions = await self._oculus.get_app_versions(app_id)
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
            pkg: AppPackage | None = await self._oculus.get_version_package(
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
        apps: dict[str, list[tuple[str, LocalApp]]] = \
            self._app_manager.get_all_by_id()
        self._logger.info("Fetching %s apps from oculus.com", len(apps))

        tasks: list[OculusApp | None] = await asyncio.gather(
            *[self._scrape_app(a, p) for a, p in apps.items()]
        )

        await self._app_manager.save()

        self._calc_average_ratings([i for i in tasks if i])
        await asyncio.gather(*[
            r.save_json(f"{AppConfig().data_path}/{r.data.id}.json")
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
        app: str,
        packages: list[tuple[str, LocalApp]]
    ) -> OculusApp | None:
        """
        Scrape details and images for a specific app.

        Returns:
        Optional[OculusApp]: The scraped OculusApp instance or None if no
            response.
        """
        if (result := await self._scrape_app_id(app)) is None:
            error: str = ErrorManager().capture(
                "ValidationError",
                "Scraping app data",
                f"No responses for: {app}",
                error_info={
                    "package": packages,
                    "id": app
                }
            )
            self._logger.warning("%s", error)
            return None

        self._handle_errors(result, packages)
        result.data.changelog = packages[0][1].change_log
        result.data.on_rookie = packages[0][1].on_rookie

        image_downloads: list[AppImage] = \
            await self._oculus.get_resources(result.data.resources)
        await self._process_images(image_downloads)

        for i in packages:
            await self._app_manager.update(
                i[0],
                result.data.app_name,
                result.data.is_available,
                result.data.is_free,
                result.data.is_demo_of is not None
            )
        return result

    async def _scrape_app_id(self, app_id: str) -> OculusApp | None:
        """
        Scrape app details and additional details for a specific app ID.

        Parameters:
        - app_id (str): The ID of the app.

        Returns:
        Optional[OculusApp]: The scraped OculusApp instance or None if no
            response.
        """
        if (app := await self._oculus.get_app_details(app_id)) is None:
            return None
        additionals: AppAdditionalDetails | None = \
            await self._oculus.get_app_additionals(app_id)
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
        except asyncio.TimeoutError as e:
            error: str = ErrorManager().capture(
                e,
                "Saving Image File",
                error_info={
                    "file_path": file_path
                }
            )
            self._logger.warning("%s", error)
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
        except asyncio.TimeoutError as e:
            error: str = ErrorManager().capture(
                e,
                "Creating Directory",
                error_info={
                    "directory": directory
                }
            )
            self._logger.warning("%s", error)
            return None
        return directory

    def _handle_errors(
        self,
        response: OculusApp,
        packages: list[tuple[str, LocalApp]]
    ) -> None:
        """
        Handle errors in the response and log them.
        """
        if len(response.errors) == 0:
            return
        for i in packages:
            error: str = ErrorManager().capture(
                "ValidationError",
                "Parsing Oculus App Response",
                f"App Response contains errors: {i[1].app_name}",
                error_info={
                    "package": i[0],
                    "local_app": i[1],
                    "errors": response.errors,
                    "data": response.data.model_dump()
                }
            )
            self._logger.warning("%s", error)
