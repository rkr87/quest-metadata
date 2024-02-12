"""
Module providing a singleton class for managing a collection of local apps.

Classes:
- AppManager: Singleton class for managing local apps.

Constants:
- APPS (str): File path for storing the serialized collection of local apps.
"""
from typing import final

from pydantic_core import ValidationError

from base.classes import Singleton
from config.app_config import AppConfig
from data.model.local.apps import LocalApp, LocalApps, LocalAppUpdate
from data.model.oculus.app_changelog import AppChangeLog
from data.model.parsed.app_item import ParsedAppItem
from data.model.rookie.releases import RookieRelease
from utils.error_manager import ErrorManager


@final
class AppManager(Singleton):
    """
    Singleton class for managing a collection of local apps.

    Attributes:
    - _apps (LocalApps): The collection of local apps.
    - _exclusion_days (int): The number of days to exclude recently updated
        apps.

    Methods:
    - get: Get the collection of local apps, optionally excluding recently
        updated ones.
    - _filter_recently_updated_apps: Filter recently updated apps from the
        collection.
    - _need_update: Check if an app needs an update based on the exclusion
        days.
    - add: Add a parsed app item to the collection.
    - _add_or_update_local_app: Add or update a local app in the collection.
    - _create_new_local_app: Create a new local app in the collection.
    - _update_existing_local_app: Update an existing local app in the
        collection.
    - _update_app_details: Update app details for an existing local app.
    - _update_additional_ids: Update additional IDs for an existing local app.
    - save: Save the collection of local apps to a JSON file.
    - update: Update information for a specific app in the collection.
    - _load_from_file: Load the collection of local apps from a JSON file.
    """

    def __init__(self, exclusion_days: int = 7) -> None:
        super().__init__()
        self._logger.info("Initialising app manager")
        config = AppConfig()
        self._file: str = f"{config.data_path}/{config.apps_filename}"
        self._apps: LocalApps = self._load_from_file()
        self._exclusion_days: int = exclusion_days

    def get(self) -> LocalApps:
        """
        Get the collection of local apps.

        Returns:
        - LocalApps: The collection of local apps.
        """
        return self._apps

    def get_all_by_id(self) -> dict[str, list[tuple[str, LocalApp]]]:
        """
        Get the collection of local apps grouped by identified id.
        """
        output: dict[str, list[tuple[str, LocalApp]]] = {}
        for k, v in self._apps.items():
            if v.id is None:
                continue
            if v.id not in output:
                output[v.id] = [(k, v)]
                continue
            if k not in output[v.id][0]:
                output[v.id].append((k, v))
        return output

    def get_app_by_id(self, app_id: str) -> tuple[str, LocalApp] | None:
        """Retrieve a local app by its unique identifier."""
        for k, v in self._apps.items():
            if v.id == app_id:
                return k, v
        return None

    def get_needs_changelog(self) -> LocalApps:
        """Get a collection of local apps that need a changelog update."""
        output: LocalApps = LocalApps()
        for key, app in self._apps.items():
            if app.change_log is None:
                output[key] = app
        return output

    def add(self, parsed_item: ParsedAppItem) -> None:
        """
        Add a parsed app item to the collection.

        Args:
        - parsed_item (ParsedAppItem): The parsed app item to add.
        """
        for package in parsed_item.packages:
            self._add_or_update_local_app(package, parsed_item)

    def _add_or_update_local_app(
        self,
        package: str,
        parsed_item: ParsedAppItem
    ) -> None:
        """
        Add or update a local app in the collection.

        Args:
        - package (str): The package name of the app.
        - parsed_item (ParsedAppItem): The parsed app item.
        """
        if package in self._apps:
            self._update_existing_local_app(package, parsed_item)
            return
        self._create_new_local_app(package, parsed_item)

    def _create_new_local_app(
        self,
        package: str,
        parsed_item: ParsedAppItem
    ) -> None:
        """
        Create a new local app in the collection.

        Args:
        - package (str): The package name of the app.
        - parsed_item (ParsedAppItem): The parsed app item.
        """
        app: LocalApp = LocalApp(
            id=parsed_item.id,
            app_name=parsed_item.name,
            max_version_date=parsed_item.max_version_date,
            max_version=parsed_item.max_version
        )
        self._apps[package] = app

    def add_changelog(self, package: str, change_log: AppChangeLog) -> bool:
        """
        Add a changelog to a local app and return a boolean based on whether
        the changelog was updated since last run.
        """
        self._apps[package].change_log = change_log.get_valid_changes()
        latest: int = change_log.get_latest_version()
        updated: bool = latest > self._apps[package].max_version
        self._apps[package].max_version = latest
        return updated

    def add_rookie_releases(
        self,
        package_name: str,
        rookie_package: list[RookieRelease]
    ) -> None:
        """
        Add Rookie release details to local app if package exists, otherwise
        create a new local app with no version details, this will ensure if
        a package mapping is added later it will be updated correctly.
        """
        if package_name in self._apps:
            self._apps[package_name].rookie_releases = rookie_package
        else:
            app: LocalApp = LocalApp(
                id=None,
                app_name=rookie_package[0].app_name,
                max_version_date=0,
                max_version=0,
                rookie_releases=rookie_package
            )
            self._apps[package_name] = app

    def _update_existing_local_app(
        self,
        package: str,
        parsed_item: ParsedAppItem
    ) -> None:
        """
        Update an existing local app in the collection.

        Args:
        - package (str): The package name of the app.
        - parsed_item (ParsedAppItem): The parsed app item.
        """
        local_app: LocalApp = self._apps[package]
        if parsed_item.name != "":
            local_app.app_name = parsed_item.name
        self._update_app_details(local_app, parsed_item)

    @staticmethod
    def _update_app_details(
        local_app: LocalApp,
        parsed_item: ParsedAppItem
    ) -> None:
        """
        Update app details for an existing local app.

        Args:
        - local_app (LocalApp): The existing local app.
        - parsed_item (ParsedAppItem): The parsed app item.
        """
        if (
            local_app.id is None or
            parsed_item.max_version_date >= local_app.max_version_date
        ):
            local_app.max_version_date = parsed_item.max_version_date
            local_app.max_version = parsed_item.max_version
            if local_app.id != parsed_item.id:
                local_app.change_log = None
                local_app.id = parsed_item.id

    async def save(self) -> None:
        """
        Save the collection of local apps to a JSON file.
        """
        await self._apps.save_json(self._file)

    async def update(
        self,
        package_name: str,
        update: LocalAppUpdate
    ) -> None:
        """
        Update information for a specific app in the collection.

        Args:
        - store_id (str): The store ID of the app.
        - is_available (bool): The availability status of the app.
        - is_free (bool): The free status of the app.
        - is_demo (bool): The demo status of the app.
        """
        if package_name in self._apps:
            self._apps[package_name].is_free = update.is_free
            self._apps[package_name].is_available = update.is_available
            self._apps[package_name].is_demo_of = update.is_demo_of
            self._apps[package_name].has_metadata = update.has_metadata
            if update.app_name != "":
                self._apps[package_name].app_name = update.app_name

    def _load_from_file(self) -> LocalApps:
        """
        Load the collection of local apps from a JSON file.

        Returns:
        - LocalApps: The loaded collection of local apps.
        """
        try:
            with open(self._file, encoding="utf8") as file:
                return LocalApps.model_validate_json(file.read())
        except (FileNotFoundError, ValidationError) as e:
            error: str = ErrorManager().capture(
                e,
                "Loading _apps.json",
                log_message="Couldn't load _apps.json - creating a new one."
            )
            self._logger.warning("%s", error)
            return LocalApps()
