"""
Module providing models for local applications.

Classes:
- LocalApp: Model for representing a local application.
- LocalApps: Dictionary-based model for a collection of local applications.
"""
from typing import Annotated

from pydantic import Field

from base.models import BaseModel, RootDictModel


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
    id: str
    additional_ids: list[str] = []
    app_name: str
    max_version_date: Annotated[int, Field(exclude=True, default=0)]
    added: str
    updated: str | None = None
    is_available: bool | None = None
    is_free: bool | None = None
    is_demo: bool | None = None


class LocalApps(RootDictModel[str, LocalApp]):
    """
    Dictionary-based model for a collection of local applications.

    Inherits from:
    - RootDictModel[str, LocalApp]
    """
