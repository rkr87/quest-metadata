"""
Module providing models for application changelogs.
"""

from typing import Annotated, Any

from pydantic import Field, field_validator, model_validator

from base.models import BaseModel, RootListModel


class AppChangeEntry(BaseModel):
    """Model for representing an application changelog entry."""
    version: str
    code: Annotated[int, Field(validation_alias='versionCode', exclude=True)]
    change_log: str | None = Field(validation_alias='changeLog')

    @model_validator(mode="before")
    @classmethod
    def flatten(cls, val: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Returns the nested node key."""
        try:
            return val['node']
        except (TypeError, KeyError):
            return val

    @field_validator("change_log", mode="before")
    @classmethod
    def set_to_none(cls, val: str) -> str | None:
        """Set empty change logs to None."""
        if val:
            return val
        return None

    class Config:
        """
        Configurations:
        - populate_by_name: Config to populate the model by name.
        """
        populate_by_name = True


class AppChangeLog(RootListModel[AppChangeEntry]):
    """List-based model for a collection of application changelog entries."""
    root: list[AppChangeEntry]

    @field_validator("root", mode="before")
    @classmethod
    def flatten(cls, val: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Flattens a dictionary structure to a list of filtered application
        changelog entry nodes.
        """
        try:
            flatten: list[dict[str, Any]] = \
                val["data"]["node"]["supportedBinaries"]["edges"]
        except (TypeError, KeyError):
            return []
        return flatten

    def get_latest_version(self) -> int:
        """Get the latest version code from the changelog."""
        if len(self.root) == 0:
            return 0
        return max(i.code for i in self.root)

    def get_valid_changes(self) -> list[AppChangeEntry]:
        """Get a list of valid changelog entries with non-empty change logs."""
        if len(self.root) == 0:
            return []
        return [i for i in self.root if i.change_log is not None]
