"""
Module providing models for Oculus database applications.

Classes:
- OculusDbApp: Model representing an Oculus database application.
- OculusDbApps: Model representing a list of Oculus database applications.
"""
from collections.abc import Callable

from pydantic import field_validator

from base.models import BaseModel, RootListModel
from helpers.string import to_camel


class OculusDbApp(BaseModel):
    """
    Model representing an Oculus database application.

    Attributes:
    - id (str): The ID of the application.
    - app_name (str): The name of the application.
    - package_name (str | None): The package name of the application.

    Methods:
    - set_none: Class method to set None if the input is empty.
    """
    id: str
    app_name: str
    package_name: str | None

    @field_validator("package_name", mode="before")
    @classmethod
    def set_none(cls, val: str | None) -> str | None:
        """
        Class method to set None if the input is empty.

        Args:
        - val (str | None): The input value.

        Returns:
        - str | None: The input value or None if it is empty.
        """
        if not val:
            return None
        return val

    class Config:
        """
        Configurations:
        - alias_generator: Custom alias generator function to convert field
            names to camelCase.
        - populate_by_name: Config to populate the model by name.
        """
        alias_generator: Callable[..., str] = to_camel
        populate_by_name = True


class OculusDbApps(RootListModel[OculusDbApp]):
    """
    Model representing a list of Oculus database applications.
    """
