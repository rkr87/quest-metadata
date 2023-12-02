from datetime import datetime, timedelta

from typing_extensions import final, overload

from base.singleton import Singleton
from data.model.local_apps import LocalApp, LocalApps

APPS: str = "./data/apps.json"


@final
class AppManager(metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]; pylint: disable=line-too-long
    '''
    Manages application information, providing methods for loading,
    updating, and saving data.
    '''

    def __init__(self, exclusion_days: int = 7) -> None:
        self._apps: LocalApps = self._load_from_file()
        self._exclusion_days: int = exclusion_days

    def get(self,
            exclude_recently_updated: bool = False) \
            -> LocalApps:
        '''
        Retrieves applications, excluding recent updates if specified.

        Args:
            exclude_recently_updated (bool):
                Whether to exclude recently updated apps.

        Returns:
            dict: Dictionary of applications.
        '''
        if not exclude_recently_updated:
            return self._apps

        output: LocalApps = LocalApps()
        for key, app in self._apps.items():
            if self._need_update(app):
                output[key] = app
        return output

    def _need_update(self, app: LocalApp) -> bool:
        '''
        Checks if an application needs an update based on the last update
        timestamp.

        Args:
            app (App): Application information.

        Returns:
            bool: True if the application needs an update, False otherwise.
        '''
        if app.updated is None:
            return True

        last_update_time: datetime = datetime.fromisoformat(app.updated)
        delta: timedelta = datetime.now() - last_update_time
        return delta.days > self._exclusion_days

    def add(self, store_id: str, package: str, app_name: str) -> None:
        '''
        Adds a new application to the list.

        Args:
            package (str): Package name of the application.
            app_name (str): Name of the application.
            store_id (str): Store ID of the application.
        '''
        if store_id not in self._apps:
            app: LocalApp = LocalApp(packages=[package],
                                     app_name=app_name,
                                     added=datetime.now().isoformat())
            self._apps[store_id] = app
        elif package not in self._apps[store_id].packages:
            self._apps[store_id].packages.append(package)

    def save(self) -> None:
        '''
        Saves the current state of applications to a file.
        '''
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
        '''
        Updates the last update timestamp for one or more applications.

        Args:
            package_name (str | List[str] | Dict[str, App]):
                Package name or list of package names or dictionary of apps.
        '''
        if isinstance(store_id, str):
            self._update(store_id)
        else:
            for item in store_id:
                self._update(item)
        self.save()

    def _update(self, store_id: str) -> None:
        '''
        Helper method to update the last update timestamp for a single
        application.

        Args:
            package_name (str): Package name of the application.
        '''
        time: str = datetime.now().isoformat()
        if store_id in self._apps:
            self._apps[store_id].updated = time

    def _load_from_file(self) -> LocalApps:
        '''
        Helper method to load application data from a file.

        Returns:
            dict: Dictionary of applications.
        '''
        try:
            with open(APPS, encoding="utf8") as file:
                data: LocalApps = LocalApps.model_validate_json(file.read())
            return data
        except FileNotFoundError:
            return LocalApps()
