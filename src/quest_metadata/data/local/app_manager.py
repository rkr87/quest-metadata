# pyright: reportMissingTypeArgument=false
"""
app_manager.py

This module defines the AppManager class for managing local apps.

AppManager:
    A singleton class for managing local apps,
    providing methods to get, add, update, and save app information.

Attributes:
    APPS (str): The file path for storing local app information.
"""
import logging
from datetime import datetime, timedelta

from typing_extensions import final, overload

from base.singleton import Singleton
from data.model.local_apps import LocalApp, LocalApps

APPS: str = "./data/apps.json"


@final
class AppManager(metaclass=Singleton):
    """
    AppManager class for managing local apps.

    Attributes:
        _apps (LocalApps): The dictionary containing local app information.
        _exclusion_days (int): The number of days to exclude recently
            updated apps.
    """

    def __init__(self, exclusion_days: int = 7) -> None:
        """
        Initialize the AppManager instance.

        Args:
            exclusion_days (int): The number of days to exclude recently
                updated apps.
        """
        logger = logging.getLogger(__name__)
        logger.info("Initialising app manager")
        self._apps: LocalApps = self._load_from_file()
        self._exclusion_days: int = exclusion_days

    def get(self,
            exclude_recently_updated: bool = False) \
            -> LocalApps:
        """
        Get local apps.

        Args:
            exclude_recently_updated (bool): Whether to exclude recently
                updated apps.

        Returns:
            LocalApps: The dictionary containing local app information.
        """
        if not exclude_recently_updated:
            return self._apps

        output: LocalApps = LocalApps()
        for key, app in self._apps.items():
            if self._need_update(app):
                output[key] = app
        return output

    def _need_update(self, app: LocalApp) -> bool:
        """
        Check if an app needs an update based on the exclusion days.

        Args:
            app (LocalApp): The local app to check.

        Returns:
            bool: True if the app needs an update, False otherwise.
        """
        if app.updated is None:
            return True

        last_update_time: datetime = datetime.fromisoformat(app.updated)
        delta: timedelta = datetime.now() - last_update_time
        return delta.days > self._exclusion_days

    def add(self, store_id: str, package: str, app_name: str) -> None:
        """
        Add a new app or update an existing app.

        Args:
            store_id (str): The ID of the app store.
            package (str): The package name of the app.
            app_name (str): The name of the app.

        Returns:
            None
        """
        if store_id not in self._apps:
            app: LocalApp = LocalApp(packages=[package],
                                     app_name=app_name,
                                     added=datetime.now().isoformat())
            self._apps[store_id] = app
        elif package not in self._apps[store_id].packages:
            self._apps[store_id].packages.append(package)

    def save(self) -> None:
        """
        Save local app information to a file.

        Returns:
            None
        """
        with open(APPS, 'w', encoding="utf-8") as file:
            text: str = self._apps.model_dump_json(
                indent=4,
                exclude_none=True,
                exclude_unset=True
            )
            file.write(text)

    @overload
    def update(self, store_id: str) -> None: ...

    @overload
    def update(self, store_id: list[str]) -> None: ...

    @overload
    def update(self, store_id: dict[str, LocalApp]) -> None: ...

    def update(self, store_id: str | list[str] | dict[str, LocalApp]) -> None:
        """
        Update the timestamp of one or more apps.

        Args:
            store_ids (str | list[str] | dict[str, LocalApp]): The ID(s) of the
                app(s) to update.

        Returns:
            None
        """
        if isinstance(store_id, str):
            self._update(store_id)
        else:
            for item in store_id:
                self._update(item)
        self.save()

    def _update(self, store_id: str) -> None:
        """
        Update the timestamp of a single app.

        Args:
            store_id (str): The ID of the app to update.

        Returns:
            None
        """
        time: str = datetime.now().isoformat()
        if store_id in self._apps:
            self._apps[store_id].updated = time

    def _load_from_file(self) -> LocalApps:
        """
        Load local app information from a file.

        Returns:
            LocalApps: The dictionary containing local app information.
        """
        try:
            with open(APPS, encoding="utf8") as file:
                data: LocalApps = LocalApps.model_validate_json(file.read())
            return data
        except FileNotFoundError:
            return LocalApps()
