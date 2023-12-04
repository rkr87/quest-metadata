# pylint: disable=too-few-public-methods
"""TODO"""
from datetime import datetime

from base.base_model import BaseModel
from data.model.meta_response import Error


class _Iarc(BaseModel):
    """TODO"""
    age_rating: str
    descriptors: list[str]
    elements: list[str]
    icon: str


class _Rating(BaseModel):
    """
    Pydantic model for representing star ratings.
    """
    rating: int
    votes: int


class Item(BaseModel):
    """TODO"""
    id: list[str]
    name: str
    app_name: str
    type_name: str
    appstore_type: str
    category: str | None
    release_date: datetime = datetime(1980, 1, 1)
    description: str
    markdown_desc: bool
    developer: str
    publisher: str
    genres: list[str]
    input_devices: list[str]
    games_modes: list[str]
    languages: list[str]
    platforms: list[str]
    player_modes: list[str]
    tags: list[str]
    rating: float = 0
    votes: int = 0
    hist: list[_Rating]
    comfort: str
    age_rating: str | None
    iarc: _Iarc | None
    platform: str
    internet_connection: str | None
    website: str
    icon: str
    banner: str
    screenshots: list[str]
    trailer: dict[str, str | None] | None
    has_ads: bool
    require_360_sensor: bool


class MetaResult(BaseModel):
    """
    Pydantic model for representing a meta result.
    """
    data: Item
    errors: list[Error] | None = None
