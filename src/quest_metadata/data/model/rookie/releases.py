
from datetime import datetime

from pydantic import Field, field_validator

from base.models import BaseModel, RootDictModel

# class RookieRelease(BaseModel):


#     class Config:
#         """
#         Configurations:
#         - populate_by_name: Config to populate the model by name.
#         """
#         populate_by_name = True


class RookieRelease(BaseModel):
    app_name: str = Field(validation_alias="\ufeffGame Name", exclude=True)
    versions: str = Field(validation_alias="Version Code")
    release_name: str = Field(validation_alias="Release Name")
    last_updated: str = Field(validation_alias="Last Updated")
    size_mb: int = Field(validation_alias="Size (MB)")
    notes: str | None = None

    @field_validator("last_updated", mode="before")
    @classmethod
    def to_iso(cls, val: str) -> str:
        try:
            to_dt: datetime = datetime.strptime(val, "%Y-%m-%d %H:%M UTC")
            return f"{to_dt.isoformat(timespec="milliseconds")}Z"
        except ValueError:
            return f"{val}Z"

    def set_release_note(self, release_name: str, note: str) -> None:
        if self.release_name == release_name:
            self.notes = note

    # @model_validator(mode="before")
    # @classmethod
    # def convert(cls, val: dict[str, str]) -> dict[str, Any]:
    #     output: dict[str, Any] = {
    #         "app_name": val["\ufeffGame Name"],
    #         "versions": {val["Version Code"]: [val]}
    #     }
    #     return output

    class Config:
        """
        Configurations:
        - populate_by_name: Config to populate the model by name.
        """
        populate_by_name = True


class Releases(RootDictModel[str, list[RookieRelease]]):
    root: dict[str, list[RookieRelease]]

    @field_validator("root", mode="before")
    @classmethod
    def convert(
        cls,
        val: list[dict[str, str]]
    ) -> dict[str, list[RookieRelease]]:
        output: dict[str, list[RookieRelease]] = {}
        for item in val:
            if (key := item["Package Name"].lower()) not in output:
                output[key] = [RookieRelease.model_validate(item)]
            else:
                output[key].append(RookieRelease.model_validate(item))
        return output

    def set_release_note(self, release_name: str, note: str) -> None:
        for package in self.root.values():
            for release in package:
                release.set_release_note(release_name, note)
