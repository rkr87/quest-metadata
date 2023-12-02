# pylint: disable=missing-class-docstring,too-few-public-methods
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, root_validator, validator

from base.root_list_model import RootListModel
from base.root_strict_model import RootFlatten
from utils.string_helper import to_iso


class BaseModel(PydanticBaseModel):
    class Config:
        extra: str = 'ignore'


class Url(RootFlatten[str]):
    pass


class IarcRating(BaseModel):
    age_rating: str = Field(..., alias='age_rating_text')
    descriptors: list[str]
    elements: list[str] = Field(..., alias='interactive_elements')
    icon: Url = Field(..., alias='small_age_rating_image')


class Iarc(RootFlatten[IarcRating]):
    _key = "iarc_rating"


class StarRating(BaseModel):
    star_rating: int
    count: int


class Ratings(RootListModel[StarRating]):
    root: list[StarRating]


class Language(RootFlatten[str]):
    _key = "name"


class AgeRating(RootFlatten[str]):
    _key = "category_name"


class Tag(RootFlatten[str]):
    _key = "display_name"


class Tags(RootFlatten[list[Tag]]):
    _key = "nodes"


class ReleaseDate(RootFlatten[str]):
    _key = "display_date"

    @validator("root")
    @classmethod
    def to_iso(cls, val: str | None) -> str | None:
        """
        Convert the meta date format to standard ISO format
        """
        if val is None:
            return val
        return to_iso(val, "%d %b %Y")


class Trailer(BaseModel):
    thumbnail: Url | None
    uri: str


class Item(BaseModel):
    id: str
    name: str = Field(..., alias='display_name')
    app_name: str = Field(..., alias='appName')
    type_name: str = Field(..., alias='__typename')
    appstore_type: str = Field(..., alias='__isAppStoreItem')
    category: str | None
    release_date: ReleaseDate = Field(..., alias='release_info')
    description: str = Field(..., alias='display_long_description')
    markdown_desc: bool = Field(..., alias='long_description_uses_markdown')
    developer: str = Field(..., alias='developer_name')
    publisher: str = Field(..., alias='publisher_name')
    genres: list[str] = Field(..., alias='genre_names')
    input_devices: list[str] = Field(..., alias='supported_input_device_names')
    games_modes: list[str] = Field(..., alias='user_interaction_mode_names')
    languages: list[Language] = Field(..., alias='supported_in_app_languages')
    platforms: list[str] = Field(..., alias='supported_platforms_i18n')
    player_modes: list[str] = Field(..., alias='supported_player_modes')
    tags: Tags = Field(..., alias='item_tags')
    ratings_hist: Ratings = Field(
        ...,
        alias='quality_rating_histogram_aggregate_all'
    )
    rating: float | None = None
    comfort: str = Field(..., alias='comfort_rating')
    age_rating: AgeRating
    iarc: Iarc = Field(..., alias='iarc_cert')
    platform: str
    internet_connection: str
    website: str = Field(..., alias='website_url')
    icon: Url = Field(..., alias='icon_image')
    banner: Url = Field(..., alias='hero')
    screenshots: list[Url]
    trailer: Trailer | None
    has_ads: bool = Field(..., alias='has_in_app_ads')
    require_360_sensor: bool = Field(..., alias='is_360_sensor_setup_required')

    @root_validator(pre=True, allow_reuse=False)
    @classmethod
    def weighted_ratings(cls, val: dict[str, Any]) -> dict[str, Any]:
        """
        Convert the meta date format to standard ISO format
        """
        ratings = val.get('quality_rating_histogram_aggregate_all')
        if ratings is None:
            return val
        votes: int = 0
        rating: int = 0
        for item in ratings:
            votes += item['count']
            rating += item['star_rating'] * item['count']
        if votes > 0:
            val['rating'] = rating / votes
        return val


class Data(RootFlatten[Item]):
    _key = "item"


class Error(BaseModel):
    message: str
    severity: str
    mids: list[str]
    path: list[int | str]


class MetaResponse(BaseModel):
    data: Data
    errors: list[Error] | None = None
