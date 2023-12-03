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
from abc import ABC
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, root_validator, validator

from base.root_flatten import RootFlatten
from base.root_list_model import RootListModel
from utils.string_utils import to_iso


class _BaseModel(ABC, PydanticBaseModel):
    """
    Base Pydantic model with ABC and PydanticBaseModel as parents.
    """
    class Config:
        """
        Set all children to ignore all keys provided that are not
        defined by the model.
        """
        extra: str = 'ignore'


class _Url(RootFlatten[str]):
    """
    Pydantic model that flattens the provided dict["uri"] key into a str.
    """
    _key = "uri"


class _IarcRating(_BaseModel):
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


class _RatingHist(_BaseModel):
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
        item = "Browse all"
        for tag in val:
            if tag.root == item:
                val.remove(tag)
        return val


class _ReleaseDate(RootFlatten[str]):
    """
    Pydantic model that flattens the provided dict["display_date"]
    key into a str and converts the provided value to standard ISO format.
    """
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


class _Trailer(_BaseModel):
    """
    Pydantic model for representing a trailer.
    """
    thumbnail: _Url | None
    uri: str


class _Item(_BaseModel):
    """
    Pydantic model for representing an item.
    """
    id: str
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
    rating: float | None
    votes: int | None
    hist: _Ratings = Field(..., alias='quality_rating_histogram_aggregate_all')
    comfort: str = Field(..., alias='comfort_rating')
    age_rating: _AgeRating
    iarc: _Iarc = Field(..., alias='iarc_cert')
    platform: str
    internet_connection: str
    website: str = Field(..., alias='website_url')
    icon: _Url = Field(..., alias='icon_image')
    banner: _Url = Field(..., alias='hero')
    screenshots: list[_Url]
    trailer: _Trailer | None
    has_ads: bool = Field(..., alias='has_in_app_ads')
    require_360_sensor: bool = Field(..., alias='is_360_sensor_setup_required')

    @root_validator(pre=True, allow_reuse=False)
    @classmethod
    def weighted_ratings(cls, val: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate the weighted average rating based on the provided histogram.

        Args:
            val (dict[str, Any]): The input dictionary containing
                the ratings histogram.

        Returns:
            dict[str, Any]: The modified dictionary with the calculated
                weighted average rating.

        Note:
            The ratings histogram should be in the format:
            [
                {"star_rating": int, "count": int},
                ...
            ]
            The weighted average rating is calculated by summing
            up the product of each star rating and its count,
            then dividing by the total count of votes.
        """
        ratings = val.get('quality_rating_histogram_aggregate_all', [])
        votes: int = sum(r['count'] for r in ratings)
        rating: int = sum(r['count'] * r['star_rating'] for r in ratings)
        val['rating'] = None if votes == 0 else rating / votes
        val['votes'] = votes
        return val


class _Data(RootFlatten[_Item]):
    """
    Pydantic model that flattens the provided dict["item"] key into an Item.
    """
    _key = "item"


class _Error(_BaseModel):
    """
    Pydantic model for representing an error.
    """
    message: str
    severity: str
    mids: list[str]
    path: list[int | str]


class MetaResponse(_BaseModel):
    """
    Pydantic model for representing a meta response.
    """
    data: _Data
    errors: list[_Error] | None = None
