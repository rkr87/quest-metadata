"""
Module providing models for application versions.

Classes:
- AppVersion: Model for representing an application version.
- AppVersions: List-based model for a collection of application versions.
"""

from typing import Any

from pydantic import Field, field_validator

from base.models import BaseModel, RootListModel
from constants.constants import BINARY_TYPE


class AppVersion(BaseModel):
    """
    Model for representing an application version.

    Attributes:
    - version (str): The version string of the application.
    - code (int): The version code of the application.
    - created_date (int): The date when the application version was created.
    """
    version: str
    code: int = Field(validation_alias='version_code')
    created_date: int


class AppVersions(RootListModel[AppVersion]):
    """
    List-based model for a collection of application versions.

    Attributes:
    - root (list[AppVersion]): The list of application versions.

    Methods:
    - flatten: Class method to flatten a dictionary structure to a list of
      filtered application version nodes.
    """
    root: list[AppVersion]

    @field_validator("root", mode="before")
    @classmethod
    def flatten(cls, val: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Flattens a dictionary structure to a list of filtered application
        version nodes.

        Args:
        - val (dict[str, Any]): The input dictionary containing application
          version nodes.

        Returns:
        - list[dict[str, Any]]: The flattened list of filtered application
          version nodes.
        """
        def check_binary(item: dict[str, Any]) -> bool:
            return (
                item['__typename'] == BINARY_TYPE and
                len(item['binary_release_channels']['nodes']) > 0
            )

        try:
            flatten: list[dict[str, Any]] = \
                val["data"]["node"]["primary_binaries"]["nodes"]
        except (TypeError, KeyError):
            return []
        return [i for i in flatten if check_binary(i)]
