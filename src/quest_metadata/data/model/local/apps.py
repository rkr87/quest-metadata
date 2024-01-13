"""
Module providing models for local applications.

Classes:
- LocalApp: Model for representing a local application.
- LocalApps: Dictionary-based model for a collection of local applications.
"""

from pydantic import Field, computed_field

from base.lists import UniqueList
from base.models import BaseModel, RootDictModel
from data.model.oculus.app_changelog import AppChangeEntry
from data.model.rookie.releases import RookieRelease


class LocalApp(BaseModel):
    """
    Model for representing a local application.

    Attributes:
    - id (str): The identifier for the local application.
    - additional_ids (list[str]): Additional identifiers for the local
        application.
    - app_name (str): The name of the local application.
    - max_version_date (Annotated[int, Field]): The maximum version date
        of the local application.
    - added (str): The date when the local application was added.
    - updated (str | None): The date when the local application was last
        updated, or None.
    - is_available (bool | None): Indicates whether the local application is
        available, or None.
    - is_free (bool | None): Indicates whether the local application is free,
        or None.
    - is_demo (bool | None): Indicates whether the local application is a demo,
        or None.
    """
    id: str | None = None
    additional_ids: UniqueList[str] = UniqueList()
    app_name: str
    max_version: int = 0
    max_version_date: int = 0
    change_log: list[AppChangeEntry] | None = Field(default=None, exclude=True)
    added: str
    updated: str | None = None
    is_available: bool | None = None
    is_free: bool | None = None
    is_demo: bool | None = None

    @computed_field  # type: ignore[misc]
    @property
    def on_rookie(self) -> bool:
        """Indicates whether the local application is available on Rookie"""
        return len(self.rookie_releases) > 0

    rookie_releases: dict[str, list[RookieRelease]] = {}


class LocalApps(RootDictModel[str, LocalApp]):
    """
    Dictionary-based model for a collection of local applications.

    Inherits from:
    - RootDictModel[str, LocalApp]
    """
