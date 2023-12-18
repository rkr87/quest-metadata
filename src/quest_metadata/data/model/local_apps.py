"""
local_apps.py

This module defines Pydantic models for representing local applications.

Usage:
    To use these models, create instances of `LocalApp` and `LocalApps` and
    interact with them as needed.

    ```python
    from local_apps import LocalApp, LocalApps

    # Create an instance of LocalApp
    my_app = LocalApp(packages=['pkg1', 'pkg2'], app_name='MyApp',
                      added='2023-01-01T00:00:00', updated=None)

    # Create an instance of LocalApps
    my_apps = LocalApps({'app1': my_app, 'app2': my_app})
    ```
"""


from pydantic import Field

from base.base_model import BaseModel
from base.root_dict_model import RootDictModel


class Logos(BaseModel):
    """
    Pydantic model for representing logos associated with a local application.
    """
    portrait: str | None = None
    landscape: str | None = None


class LocalApp(BaseModel):
    """
    Pydantic model for representing a local application.
    """
    store_ids: list[str]
    app_name: str
    added: str
    updated: str | None = None
    is_available: bool | None = None
    is_free: bool | None = None
    is_demo: bool | None = None
    logos: Logos | None = Field(default=None, exclude=True)


class LocalApps(RootDictModel[str, LocalApp]):
    """
    Pydantic model for representing a dictionary of local applications.
    """
