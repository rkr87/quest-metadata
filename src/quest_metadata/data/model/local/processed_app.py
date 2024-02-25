"""
Module providing models for previously processed apps.
"""
from typing import Any

from pydantic import model_validator

from base.models import BaseModel

# class ProcessedAppChangeEntry(BaseModel):
#     """Model for representing an application changelog entry."""
#     version: str
#     change_log: str | None

# class ProcessedIarc(BaseModel):
#     """Model for IARC rating details."""
#     age_rating: str | None
#     descriptors: list[str]
#     elements: list[str]


class ProcessedApp(BaseModel):
    """Model for representing an application item."""
    id: str
    app_name: str
    release_date: str
    description: str
    developer: str
    publisher: str
    genres: list[str]
    devices: list[str]
    modes: list[str]
    languages: list[str]
    platforms: list[str]
    player_modes: list[str]
    tags: list[str]
    comfort: str
    # iarc: ProcessedIarc
    internet_connection: str
    website: str
    app_images: dict[str, str | None]
    # changelog: list[ProcessedAppChangeEntry]
    keywords: list[str]
    on_rookie: bool
    category: str
    votes: int
    rating: float
    weighted_rating: float
    last_update: int = 0
    general_update: int = 0
    device_update: int = 0
    genre_update: int = 0
    keyword_update: int = 0
    language_update: int = 0
    mode_update: int = 0
    platform_update: int = 0
    player_mode_update: int = 0
    tag_update: int = 0
    # changelog_update: datetime = datetime(2024,1,1)

    @model_validator(mode="before")
    @classmethod
    def get_data(cls, val: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """unnest data"""
        return val['data']
