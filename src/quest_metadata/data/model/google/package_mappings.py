
from datetime import datetime

from pydantic import Field, field_validator

from base.models import BaseModel, RootListModel


class PackageMapping(BaseModel):
    """Model for representing a package mapping."""
    timestamp: datetime = Field(validation_alias="Timestamp")
    name: str = Field(validation_alias="app_title")
    package: str = Field(validation_alias="package_name")
    store_id: str = Field(validation_alias="meta_store_id")

    @field_validator("store_id", mode="before")
    @classmethod
    def to_str(cls, val: int) -> str:
        """Convert store_id to string."""
        return str(val)

    @field_validator("timestamp", mode="before")
    @classmethod
    def to_datetime(cls, val: str) -> datetime:
        """Convert timestamp string to datetime."""
        return datetime.strptime(val, "%m/%d/%Y %H:%M:%S")


class PackageMappings(RootListModel[PackageMapping]):
    """List-based model for a collection of package mappings."""
    root: list[PackageMapping]
