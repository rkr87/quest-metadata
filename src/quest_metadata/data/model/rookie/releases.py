

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from base.models import BaseModel, RootDictModel


class RookieRelease(BaseModel):
    release_name: str = Field(validation_alias="Release Name")
    last_updated: datetime = Field(validation_alias="Last Updated")
    size_mb: int = Field(validation_alias="Size (MB)")
    notes: str | None = None

    @field_validator("last_updated", mode="before")
    @classmethod
    def to_datetime(cls, val: str) -> datetime:
        try:
            return datetime.strptime(val, "%Y-%m-%d %H:%M UTC")
        except ValueError:
            return datetime.fromisoformat(val)

    def set_release_note(self, release_name: str, note: str) -> None:
        if self.release_name == release_name:
            self.notes = note

    class Config:
        """
        Configurations:
        - populate_by_name: Config to populate the model by name.
        """
        populate_by_name = True


class RookiePackage(BaseModel):
    app_name: str
    versions: dict[str, list[RookieRelease]]

    @model_validator(mode="before")
    @classmethod
    def convert(cls, val: dict[str, str]) -> dict[str, Any]:
        output: dict[str, Any] = {
            "app_name": val["\ufeffGame Name"],
            "versions": {val["Version Code"]: [val]}
        }
        return output

    def set_release_note(self, release_name: str, note: str) -> None:
        for releases in self.versions.values():
            for release in releases:
                release.set_release_note(release_name, note)

    class Config:
        """
        Configurations:
        - populate_by_name: Config to populate the model by name.
        """
        populate_by_name = True


class Releases(RootDictModel[str, RookiePackage]):
    root: dict[str, RookiePackage]

    @field_validator("root", mode="before")
    @classmethod
    def convert(cls, val: list[dict[str, str]]) -> dict[str, RookiePackage]:
        output: dict[str, RookiePackage] = {}
        for item in val:
            version: str = item['Version Code']
            if (key := item["Package Name"].lower()) not in output:
                output[key] = RookiePackage.model_validate(item)
            elif version not in output[key].versions:
                output[key].versions[version] = [RookieRelease.model_validate(item)]
            else:
                output[key].versions[version].append(RookieRelease.model_validate(item))
        return output

    def set_release_note(self, release_name: str, note: str) -> None:
        for package in self.root.values():
            package.set_release_note(release_name, note)
