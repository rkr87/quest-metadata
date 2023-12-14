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

from pydantic import AliasPath, Field, computed_field, validator

from base.base_model import BaseModel


class _IarcRating(BaseModel):
    """
    Pydantic model for representing IARC rating.
    """
    age_rating: str = Field(..., validation_alias='age_rating_text')
    descriptors: list[str]
    elements: list[str] = Field(..., validation_alias='interactive_elements')
    icon: str = Field(
        ...,
        validation_alias=AliasPath('small_age_rating_image', 'uri')
    )


class RatingHist(BaseModel):
    """
    Pydantic model for representing star ratings.
    """
    rating: int = Field(..., validation_alias='star_rating')
    votes: int = Field(..., validation_alias='count')


class _Trailer(BaseModel):
    """
    Pydantic model for representing a trailer.
    """
    thumbnail: str | None = Field(
        default=None,
        validation_alias=AliasPath('thumbnail', 'uri')
    )
    url: str = Field(..., validation_alias='uri')


class Item(BaseModel):
    """
    Pydantic model for representing an item.
    """
    ids: list[str] = Field(..., validation_alias='id')
    name: str = Field(..., validation_alias='display_name')
    app_name: str = Field(..., validation_alias='appName')
    type_name: str = Field(..., validation_alias='__typename')
    appstore_type: str = Field(..., validation_alias='__isAppStoreItem')
    category: str | None
    release_date: datetime = Field(
        default=datetime(1980, 1, 1),
        validation_alias=AliasPath('release_info', 'display_date')
    )
    description: str = Field(..., validation_alias='display_long_description')
    markdown_desc: bool = Field(
        ...,
        validation_alias='long_description_uses_markdown'
    )
    developer: str = Field(..., validation_alias='developer_name')
    publisher: str = Field(..., validation_alias='publisher_name')
    genres: list[str] = Field(..., validation_alias='genre_names')
    input_devices: list[str] = Field(
        ...,
        validation_alias='supported_input_device_names'
    )
    games_modes: list[str] = Field(
        ...,
        validation_alias='user_interaction_mode_names'
    )
    languages: list[str] = Field(
        ...,
        validation_alias='supported_in_app_languages'
    )
    platforms: list[str] = Field(
        ...,
        validation_alias='supported_platforms_i18n'
    )
    player_modes: list[str] = Field(
        ...,
        validation_alias='supported_player_modes'
    )
    tags: list[str] = Field(
        ...,
        validation_alias=AliasPath('item_tags', 'nodes')
    )
    hist: list[RatingHist] = Field(
        ...,
        validation_alias='quality_rating_histogram_aggregate_all'
    )
    comfort: str = Field(..., validation_alias='comfort_rating')
    age_rating: str | None = Field(
        default=None,
        validation_alias=AliasPath('age_rating', 'category_name')
    )
    iarc: _IarcRating | None = Field(
        default=None,
        validation_alias=AliasPath('iarc_cert', 'iarc_rating')
    )
    platform: str
    internet_connection: str | None
    website: str = Field(..., validation_alias='website_url')
    icon: str = Field(..., validation_alias=AliasPath('icon_image', 'uri'))
    banner: str = Field(..., validation_alias=AliasPath('hero', 'uri'))
    screenshots: list[str]
    trailer: _Trailer | None
    has_ads: bool = Field(..., validation_alias='has_in_app_ads')
    require_360_sensor: bool = Field(
        ...,
        validation_alias='is_360_sensor_setup_required'
    )
    price_gbp: int | None = Field(
        default=None,
        validation_alias=AliasPath("current_offer", "price", "offset_amount"),
        exclude=True
    )

    @computed_field  # type: ignore[misc]
    @property
    def votes(self) -> int:
        """
        Calculate the total number of votes for the item.

        Returns:
            int: The total number of votes.
        """
        return sum(r.votes for r in self.hist)  # pylint: disable=not-an-iterable

    @computed_field  # type: ignore[misc]
    @property
    def rating(self) -> float:
        """
        Calculate the overall rating for the item based on votes and
        individual ratings.

        Returns:
            float: The overall rating.
        """
        if self.votes != 0:
            rating: int = sum(r.votes * r.rating for r in self.hist)  # pylint: disable=not-an-iterable
            return rating / self.votes
        return 0

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        """
        Check if the item is available for purchase.

        Returns:
            bool: True if available, False otherwise.
        """
        return self.price_gbp is not None

    @computed_field  # type: ignore[misc]
    @property
    def is_free(self) -> bool:
        """
        Check if the item is available for free.

        Returns:
            bool: True if free, False otherwise.
        """
        return self.price_gbp is not None and self.price_gbp == 0

    @validator("ids", pre=True)
    @classmethod
    def id_to_list(cls, val: str) -> list[str]:
        """
        Convert a single item ID to a list of item IDs.

        Args:
            val (str): The item ID.

        Returns:
            list[str]: List containing the item ID.
        """
        return [val]

    @validator("release_date", pre=True)
    @classmethod
    def to_datetime(cls, val: str | None) -> datetime:
        """
        Convert a date string to a datetime object.

        Args:
            val (str | None): The date string or None if not available.

        Returns:
            datetime: The converted datetime object.
        """
        default = datetime(1980, 1, 1)
        if val is None:
            return default

        date_formats: list[str] = ["%d %b %Y", "%b, %d %Y"]
        for fmt in date_formats:
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                pass
        return default

    @validator("tags", pre=True)
    @classmethod
    def parse_tags(cls, val: list[dict[str, str]]) -> list[str]:
        """
        Parse and filter item tags.

        Args:
            val (list[dict[str, str]]): List of dictionaries containing
                tag information.

        Returns:
            list[str]: List of filtered item tags.
        """
        remove: list[str] = [
            "browse all",
            "try before you buy",
            "nik_test",
            "stephrhee"
        ]
        key = 'display_name'
        return [x[key] for x in val if x[key].lower() not in remove]

    @validator("languages", pre=True)
    @classmethod
    def parse_languages(cls, val: list[dict[str, str]]) -> list[str]:
        """
        Parse supported in-app languages.

        Args:
            val (list[dict[str, str]]): List of dictionaries containing
                language information.

        Returns:
            list[str]: List of supported in-app languages.
        """
        return [x['name'] for x in val]

    @validator("screenshots", pre=True)
    @classmethod
    def parse_screenshots(cls, val: list[dict[str, str]]) -> list[str]:
        """
        Parse item screenshots.

        Args:
            val (list[dict[str, str]]): List of dictionaries containing
                screenshot information.

        Returns:
            list[str]: List of item screenshots.
        """
        return [x['uri'] for x in val]


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
    data: Item = Field(..., validation_alias=AliasPath("data", "item"))
    errors: list[Error] | None = None
