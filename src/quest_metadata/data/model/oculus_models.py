"""
Module providing models for handling Oculus app data.

Classes:
- LatestBinary: Model representing the latest supported binary.
- BinaryPackage: Model representing binary package information.
- OculusApp: Model representing an Oculus app.
- OculusApps: List model for OculusApp instances.
"""
from collections.abc import Callable

from pydantic import AliasPath, Field, field_validator

from base.base_model import BaseModel
from base.root_list_model import RootListModel
from utils.string_utils import to_camel


class LatestBinary(BaseModel):
    """
    Model representing the latest supported binary.
    """
    _path: list[str | int] = [
        "node", "release_channels", "nodes", 0, "latest_supported_binary"
    ]
    version_code: int | None = Field(
        default=None,
        validation_alias=AliasPath("data", *_path, "version_code")
    )
    type_name: str | None = Field(
        default=None,
        validation_alias=AliasPath("data", *_path, "__typename")
    )


class BinaryPackage(BaseModel):
    """
    Model representing binary package information.
    """
    package_name: str | None = Field(default=None, validation_alias=AliasPath(
        "data", "app_binary_info", "info", 0, 'binary', 'package_name'
    ))


class OculusApp(BaseModel):
    """
    Model representing an Oculus app.
    """
    id: str
    app_name: str
    package_name: str | None

    @field_validator("package_name", mode="before")
    @classmethod
    def set_none(cls, val: str | None) -> str | None:
        """
        Sets None if the value is an empty string.
        """
        if isinstance(val, str) and val == "":
            return None
        return val

    class Config:
        """
        Configuration settings for the OculusApp model.
        """
        alias_generator: Callable[..., str] = to_camel
        populate_by_name = True


class OculusApps(RootListModel[OculusApp]):
    """
    List model for OculusApp instances.
    """
