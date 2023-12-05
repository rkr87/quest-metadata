# pylint: disable=too-few-public-methods
"""
meta_models.py

This module defines Pydantic models for handling meta responses.

Usage:
    To use these models, create instances of `MetaResponse`, `Item`, and other
    relevant models as needed.

    ```python
    from meta_models import MetaResponse, Item

    # Create an instance of MetaResponse
    response = MetaResponse(data=my_data)

    # Access item from the response
    ratings = response.data.ratings
    ```
"""
from datetime import datetime

from pydantic import Field, validator

from base.base_model import BaseModel
from base.root_flatten import RootFlatten
from base.root_list_model import RootListModel


class _Url(RootFlatten[str]):
    """
    Pydantic model that flattens the provided dict["uri"] key into a str.
    """
    _key = "uri"


class _IarcRating(BaseModel):
    """
    Pydantic model for representing IARC rating.
    """
    age_rating: str = Field(..., alias='age_rating_text')
    descriptors: list[str]
    elements: list[str] = Field(..., alias='interactive_elements')
    icon: _Url = Field(..., alias='small_age_rating_image')


class _Iarc(RootFlatten[_IarcRating]):
    """
    Pydantic model that flattens the provided dict["iarc_rating"]
    key into a IarcRating class.
    """
    _key = "iarc_rating"


class _RatingHist(BaseModel):
    """
    Pydantic model for representing star ratings.
    """
    rating: int = Field(..., alias='star_rating')
    votes: int = Field(..., alias='count')


class _Ratings(RootListModel[_RatingHist]):
    """
    Pydantic model for representing a list of star ratings.
    """
    root: list[_RatingHist]


class _Language(RootFlatten[str]):
    """
    Pydantic model that flattens the provided dict["name"] key into a str.
    """
    _key = "name"


class _AgeRating(RootFlatten[str]):
    """
    Pydantic model that flattens the provided dict["category_name"]
    key into a str.
    """
    _key = "category_name"


class _Tag(RootFlatten[str]):
    """
    Pydantic model that flattens the provided dict["display_name"]
    key into a str.
    """
    _key = "display_name"


class _Tags(RootFlatten[list[_Tag]]):
    """
    Pydantic model that flattens the provided dict["nodes"]
    key into a list of Tags.
    """
    _key = "nodes"

    @validator("root")
    @classmethod
    def remove_item(cls, val: list[_Tag] | None) -> list[_Tag] | None:
        """
        Remove the "Browse all" tag from the list of tags
        """
        if val is None:
            return None
        items_to_remove: list[str] = [
            "browse all",
            "try before you buy",
            "nik_test",
            "stephrhee"
        ]
        for tag in val:
            if tag.root is not None and tag.root.lower() in items_to_remove:
                val.remove(tag)
        return val


class _ReleaseDate(RootFlatten[datetime]):
    """
    Pydantic model that flattens the provided dict["display_date"]
    key into a str and converts the provided value to standard ISO format.
    """
    _key = "display_date"

    @validator("root")
    @classmethod
    def to_datetime(cls, val: str | None) -> datetime:
        """
        Convert the meta date format to datetime
        """
        default_date = datetime(1980, 1, 1)
        try:
            return datetime.strptime(val, "%d %b %Y") if val else default_date
        except ValueError:
            return default_date


class _Trailer(BaseModel):
    """
    Pydantic model for representing a trailer.
    """
    thumbnail: _Url | None
    uri: str


class _IdList(RootListModel[str]):
    """
    Pydantic Model for merging multiple store_ids into a list.
    """
    @validator("root", pre=True)
    @classmethod
    def make_list(cls, val: str) -> list[str]:
        """
        Transform store_id into a list as some packages are listed on the store more than once.
        """
        return [val]


class _Item(BaseModel):
    """
    Pydantic model for representing an item.
    """
    id: _IdList
    name: str = Field(..., alias='display_name')
    app_name: str = Field(..., alias='appName')
    type_name: str = Field(..., alias='__typename')
    appstore_type: str = Field(..., alias='__isAppStoreItem')
    category: str | None
    release_date: _ReleaseDate = Field(..., alias='release_info')
    description: str = Field(..., alias='display_long_description')
    markdown_desc: bool = Field(..., alias='long_description_uses_markdown')
    developer: str = Field(..., alias='developer_name')
    publisher: str = Field(..., alias='publisher_name')
    genres: list[str] = Field(..., alias='genre_names')
    input_devices: list[str] = Field(..., alias='supported_input_device_names')
    games_modes: list[str] = Field(..., alias='user_interaction_mode_names')
    languages: list[_Language] = Field(..., alias='supported_in_app_languages')
    platforms: list[str] = Field(..., alias='supported_platforms_i18n')
    player_modes: list[str] = Field(..., alias='supported_player_modes')
    tags: _Tags = Field(..., alias='item_tags')
    rating: float = 0
    votes: int = 0
    hist: _Ratings = Field(..., alias='quality_rating_histogram_aggregate_all')
    comfort: str = Field(..., alias='comfort_rating')
    age_rating: _AgeRating
    iarc: _Iarc = Field(..., alias='iarc_cert')
    platform: str
    internet_connection: str | None
    website: str = Field(..., alias='website_url')
    icon: _Url = Field(..., alias='icon_image')
    banner: _Url = Field(..., alias='hero')
    screenshots: list[_Url]
    trailer: _Trailer | None
    has_ads: bool = Field(..., alias='has_in_app_ads')
    require_360_sensor: bool = Field(..., alias='is_360_sensor_setup_required')


class _Data(RootFlatten[_Item]):
    """
    Pydantic model that flattens the provided dict["item"] key into an Item.
    """
    _key = "item"


class Error(BaseModel):
    """
    Pydantic model for representing an error.
    """
    message: str
    severity: str
    mids: list[str]
    path: list[int | str]


class MetaResponse(BaseModel):
    """
    Pydantic model for representing a meta response.
    """
    data: _Data
    errors: list[Error] | None = None
