"""
meta_app.py

This module defines Pydantic models for handling a meta app response.

Usage:
    To use these models, create instances of `MetaApp`, `Item`, and other
    relevant models as needed.

    ```python
    from meta_models import MetaApp, Item
    app = MetaApp(data=my_data)
    ratings = app.data.ratings
    ```
"""
from datetime import datetime
from logging import Logger, getLogger
from typing import Annotated, ClassVar

from pydantic import AliasPath, Field, computed_field, validator

from base.base_model import BaseModel
from data.model.meta_models import MetaError, MetaResource
from data.model.store_section import StoreLogos


class _IarcRating(BaseModel):
    """
    Pydantic model for representing IARC rating.
    """
    age_rating: str = Field(validation_alias='age_rating_text')
    descriptors: list[str]
    elements: list[str] = Field(validation_alias='interactive_elements')
    iarc_icon: MetaResource = Field(
        validation_alias=AliasPath('small_age_rating_image', 'uri')
    )


class RatingHist(BaseModel):
    """
    Pydantic model for representing star ratings.
    """
    rating: int = Field(validation_alias='star_rating')
    votes: int = Field(validation_alias='count')


class Item(BaseModel):
    """
    Pydantic model for representing an item.
    """
    global_rating: ClassVar[float] = 0
    global_votes: ClassVar[int] = 0
    lower_quartile_votes: ClassVar[float] = 0

    id: str
    additional_ids: list[str] | None = None
    name: str = Field(validation_alias='display_name')
    app_name: str = Field(validation_alias='appName')
    type_name: str = Field(validation_alias='__typename')
    appstore_type: str = Field(validation_alias='__isAppStoreItem')
    category: str | None
    release_date: datetime = Field(
        default=datetime(1980, 1, 1),
        validation_alias=AliasPath('release_info', 'display_date')
    )
    description: str = Field(validation_alias='display_long_description')
    markdown: bool = Field(validation_alias='long_description_uses_markdown')
    developer: str | None = Field(validation_alias='developer_name')
    publisher: str = Field(validation_alias='publisher_name')
    genres: list[str] = Field(validation_alias='genre_names')
    devices: list[str] = Field(validation_alias='supported_input_device_names')
    modes: list[str] = Field(validation_alias='user_interaction_mode_names')
    languages: list[str] = Field(validation_alias='supported_in_app_languages')
    platforms: list[str] = Field(validation_alias='supported_platforms_i18n')
    player_modes: list[str] = Field(validation_alias='supported_player_modes')
    tags: list[str] = Field(validation_alias=AliasPath('item_tags', 'nodes'))
    hist: Annotated[
        list[RatingHist],
        Field(validation_alias='quality_rating_histogram_aggregate_all')
    ]
    comfort: str = Field(validation_alias='comfort_rating')
    age_rating: str | None = Field(
        default=None,
        validation_alias=AliasPath('age_rating', 'category_name')
    )
    iarc: Annotated[_IarcRating | None, Field(
        default=None,
        validation_alias=AliasPath('iarc_cert', 'iarc_rating')
    )]
    platform: str
    internet_connection: str | None
    website: str = Field(validation_alias='website_url')
    icon: MetaResource = Field(validation_alias=AliasPath('icon_image', 'uri'))
    banner: MetaResource = Field(validation_alias=AliasPath('hero', 'uri'))
    logo_portrait: MetaResource | None = None
    logo_landscape: MetaResource | None = None
    logo_square: MetaResource | None = None
    has_ads: bool = Field(validation_alias='has_in_app_ads')
    sensor_req: bool = Field(validation_alias='is_360_sensor_setup_required')
    price: int | None = Field(
        default=None,
        validation_alias=AliasPath("current_offer", "price", "offset_amount"),
        exclude=True
    )
    is_demo_of: str | None = Field(
        default=None,
        validation_alias=AliasPath("is_demo_of", "id"),
    )

    @computed_field  # type: ignore[misc]
    @property
    def votes(self) -> int:
        """
        Calculate the total number of votes for the item.

        Returns:
            int: The total number of votes.
        """
        return sum(r.votes for r in self.hist)

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
            rating: int = sum(r.votes * r.rating for r in self.hist)
            return round(rating / self.votes, 6)
        return 0

    @computed_field  # type: ignore[misc]
    @property
    def weighted_rating(self) -> float:
        """
        Calculate the weighted rating for the item based on a combination of
        individual ratings, total votes, and a global average.

        The weighted rating is computed using the following formula:
            (item_rating * item_votes + global_avg * confidence) /
                (item_votes + confidence)

        Returns:
            float: The weighted rating for the item.
        """
        m: float = Item.global_rating / Item.global_votes
        c: float = max(Item.lower_quartile_votes, 100)
        v: float = max(self.votes, c)
        return round((self.rating * v + m * c) / (v + c), 6)

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        """
        Check if the item is available for purchase.

        Returns:
            bool: True if available, False otherwise.
        """
        return self.price is not None

    @computed_field  # type: ignore[misc]
    @property
    def is_free(self) -> bool:
        """
        Check if the item is available for free.

        Returns:
            bool: True if free, False otherwise.
        """
        return self.price is not None and self.price == 0

    @property
    def resources(self) -> dict[str, MetaResource]:
        """
        Get a list of MetaResources associated with the item.

        Returns:
            list[MetaResource]: List of MetaResources.
        """
        consol: dict[str, MetaResource] = {
            "icon": self.icon,
            "banner": self.banner
        }
        if self.iarc is not None:
            consol['iarc_icon'] = self.iarc.iarc_icon
        if self.logo_portrait is not None:
            consol['logo_portrait'] = self.logo_portrait
        if self.logo_landscape is not None:
            consol['logo_landscape'] = self.logo_landscape
        if self.logo_square is not None:
            consol['logo_square'] = self.logo_square
        return consol

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

        date_formats: list[str] = [
            "%d %b %Y",
            "%b %d, %Y",
            "%b %Y"
        ]
        for fmt in date_formats:
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                pass
        logger: Logger = getLogger(__name__)
        logger.info("Unable to parse date: %s", val)
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


class MetaApp(BaseModel):
    """
    Pydantic model for representing a meta app.
    """
    package: str | None = None
    data: Annotated[Item, Field(validation_alias=AliasPath("data", "item"))]
    errors: list[MetaError] | None = None

    def attach_logos(self, logos: StoreLogos) -> None:
        """
        Attach logos to the meta app data.

        Args:
            logos (StoreLogos): The StoreLogos instance containing logos.
        """
        self.data.logo_landscape = logos.landscape
        self.data.logo_portrait = logos.portrait
        self.data.logo_square = logos.square
