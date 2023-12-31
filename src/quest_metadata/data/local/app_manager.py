"""
Module providing a singleton class for managing a collection of local apps.

Classes:
- AppManager: Singleton class for managing local apps.

Constants:
- APPS (str): File path for storing the serialized collection of local apps.
"""
from datetime import datetime, timedelta

from pydantic_core import ValidationError
from typing_extensions import final

from base.classes import Singleton
from constants.constants import DATA
from data.model.local.apps import LocalApp, LocalApps
from data.model.parsed.app_item import ParsedAppItem

APPS: str = f"{DATA}_apps.json"


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
        self._apps: LocalApps = self._load_from_file()
        self._exclusion_days: int = exclusion_days

    def get(self, exclude_recently_updated: bool = False) -> LocalApps:
        """
        Get the collection of local apps.

        Args:
        - exclude_recently_updated (bool): Flag to exclude recently updated
            apps.

        Returns:
        - LocalApps: The collection of local apps.
        """
        if exclude_recently_updated:
            return self._filter_recently_updated_apps()
        return self._apps

    def _filter_recently_updated_apps(self) -> LocalApps:
        """
        Filter recently updated apps from the collection.

        Returns:
        - LocalApps: The filtered collection of local apps.
        """
        output: LocalApps = LocalApps()
        for key, app in self._apps.items():
            if self._need_update(app):
                output[key] = app
        return output

    def _need_update(self, app: LocalApp) -> bool:
        """
        Check if an app needs an update based on the exclusion days.

        Args:
        - app (LocalApp): The local app to check.

        Returns:
        - bool: True if the app needs an update, False otherwise.
        """
        if app.updated is None:
            return True

        last_update_time: datetime = datetime.fromisoformat(app.updated)
        delta: timedelta = datetime.now() - last_update_time
        return delta.days > self._exclusion_days

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
            additional_ids=[],
            app_name=parsed_item.name,
            added=datetime.now().isoformat(),
            max_version_date=parsed_item.max_version_date
        )
        self._apps[package] = app

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
        additional_ids: list[str] = local_app.additional_ids or []
        if parsed_item.id not in additional_ids:
            additional_ids.append(parsed_item.id)
        if parsed_item.max_version_date >= local_app.max_version_date:
            self._update_app_details(local_app, parsed_item, additional_ids)
        self._update_additional_ids(local_app, additional_ids)

    @staticmethod
    def _update_app_details(
        local_app: LocalApp,
        parsed_item: ParsedAppItem,
        additional_ids: list[str]
    ) -> None:
        """
        Update app details for an existing local app.

        Args:
        - local_app (LocalApp): The existing local app.
        - parsed_item (ParsedAppItem): The parsed app item.
        - additional_ids (list[str]): The list of additional IDs.
        """
        local_app.max_version_date = parsed_item.max_version_date
        if local_app.id not in additional_ids:
            additional_ids.append(local_app.id)
        local_app.id = parsed_item.id

    @staticmethod
    def _update_additional_ids(
        local_app: LocalApp,
        additional: list[str]
    ) -> None:
        """
        Update additional IDs for an existing local app.

        Args:
        - local_app (LocalApp): The existing local app.
        - additional (list[str]): The list of additional IDs.
        """
        if local_app.id in additional:
            additional.remove(local_app.id)
        local_app.additional_ids = additional

    async def save(self) -> None:
        """
        Save the collection of local apps to a JSON file.
        """
        await self._apps.save_json(APPS)

    async def update(
        self,
        store_id: str,
        is_available: bool,
        is_free: bool,
        is_demo: bool
    ) -> None:
        """
        Update information for a specific app in the collection.

        Args:
        - store_id (str): The store ID of the app.
        - is_available (bool): The availability status of the app.
        - is_free (bool): The free status of the app.
        - is_demo (bool): The demo status of the app.
        """
        time: str = datetime.now().isoformat()
        if store_id in self._apps:
            self._apps[store_id].updated = time
            self._apps[store_id].is_free = is_free
            self._apps[store_id].is_available = is_available
            self._apps[store_id].is_demo = is_demo

    def _load_from_file(self) -> LocalApps:
        """
        Load the collection of local apps from a JSON file.

        Returns:
        - LocalApps: The loaded collection of local apps.
        """
        try:
            with open(APPS, encoding="utf8") as file:
                return LocalApps.model_validate_json(file.read())
        except (FileNotFoundError, ValidationError):
            self._logger.info("Failed to open %s, creating new version.", APPS)
            return LocalApps()
