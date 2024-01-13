"""
Module providing models for AppLab applications.
"""
from pydantic import Field, field_validator

from base.models import BaseModel, RootListModel


class AppLabApp(BaseModel):
    """
    Model representing an AppLab application.
    """
    id: str = Field(validation_alias="app_link")
    app_name: str

    @field_validator("id", mode="before")
    @classmethod
    def extract_id(cls, val: str) -> str:
        """Extract store id from url"""
        return \
            val.replace("https://www.meta.com/experiences/", "")


class AppLabApps(RootListModel[AppLabApp]):
    """
    Model representing a list of AppLab applications.
    """
