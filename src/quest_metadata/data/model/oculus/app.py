"""
Module providing models for Oculus applications.

Classes:
- _IarcRating: Model for IARC rating details.
- RatingHist: Model for rating histogram details.
- Item: Model for representing an Oculus application item.
- Error: Model for representing errors.
- OculusApp: Model for representing an Oculus application.
"""
from datetime import datetime
from logging import Logger, getLogger
from typing import Annotated, Any, ClassVar

from pydantic import (AliasPath, Field, computed_field, field_validator,
                      model_validator, validator)

from base.models import BaseModel
from data.model.oculus.app_additionals import (AppAdditionalDetails, AppImage,
                                               AppImages, Translation)


class _IarcRating(BaseModel):
    """
    Model for IARC rating details.

    Attributes:
    - age_rating (str | None): The age rating text.
    - descriptors (list[str]): The list of descriptors.
    - elements (list[str]): The list of interactive elements.
    - iarc_icon (AppImage | None): The IARC icon image.

    Methods:
    - add_type: Class method to add the type attribute to iarc_icon.
    - handle_none: Class method to handle None values.
    """
    age_rating: str | None = \
        Field(validation_alias='age_rating_text', default=None)
    descriptors: list[str] = []
    elements: list[str] = \
        Field(validation_alias='interactive_elements', default=[])
    iarc_icon: AppImage | None = Field(
        validation_alias='small_age_rating_image',
        default=None
    )

    @field_validator("iarc_icon", mode="before")
    @classmethod
    def add_type(cls, val: dict[str, Any]) -> dict[str, Any]:
        """
        Class method to add the type attribute to iarc_icon.

        Args:
        - val (dict[str, Any]): The input dictionary.

        Returns:
        - dict[str, Any]: The modified dictionary.
        """
        val['type'] = 'iarc_icon'
        return val

    @model_validator(mode="before")
    @classmethod
    def handle_none(cls, val: dict[str, Any] | None) -> dict[str, Any]:
        """
        Class method to handle None values.

        Args:
        - val (dict[str, Any] | None): The input dictionary.

        Returns:
        - dict[str, Any]: The modified dictionary or an empty dictionary.
        """
        return val if val else {}


class RatingHist(BaseModel):
    """
    Model for rating histogram details.

    Attributes:
    - rating (int): The rating value.
    - votes (int): The number of votes.
    """
    rating: int = Field(validation_alias='star_rating')
    votes: int = Field(validation_alias='count')


class Item(BaseModel):
    """
    Model for representing an Oculus application item.

    Attributes:
    - global_average_rating (ClassVar[float]): Class variable for global
        average rating.
    - vote_confidence (ClassVar[float]): Class variable for vote confidence.
    - id (str): The ID of the item.
    - additional_ids (list[str]): The list of additional IDs.
    - name (str): The display name of the item.
    - app_name (str): The application name.
    - type_name (str): The type name.
    - appstore_type (str): The appstore type.
    - category (str | None): The category of the item.
    - release_date (datetime): The release date of the item.
    - description (str): The display long description.
    - markdown (bool): Indicates if Markdown is used in the long description.
    - developer (str | None): The developer name.
    - publisher (str): The publisher name.
    - genres (list[str]): The list of genre names.
    - devices (list[str]): The list of supported input device names.
    - modes (list[str]): The list of user interaction mode names.
    - languages (list[str]): The list of supported in-app languages.
    - platforms (list[str]): The list of supported platforms.
    - player_modes (list[str]): The list of supported player modes.
    - tags (list[str]): The list of tags.
    - hist (Annotated[list[RatingHist]]): The annotated list of rating
        histograms.
    - comfort (str): The comfort rating.
    - age_rating (str | None): The age rating category name.
    - iarc (Annotated[_IarcRating]): The annotated IARC rating details.
    - platform (str): The platform.
    - internet_connection (str | None): The internet connection information.
    - website (str): The website URL.
    - app_images (AppImages): The collection of application images.
    - translations (list[Translation] | None): The list of translation details.
    - keywords (list[str]): The list of keywords.
    - has_ads (bool): Indicates if the item has in-app ads.
    - sensor_req (bool): Indicates if a 360 sensor setup is required.
    - price (int | None): The current offer price offset amount.
    - is_demo_of (str | None): The ID of the item if it is a demo.

    Methods:
    - set_additional_details: Method to set additional details from an
        AppAdditionalDetails instance.
    - resources: Property to get a list of AppImage resources.
    - votes: Computed property to get the sum of votes.
    - rating: Computed property to get the average rating.
    - weighted_rating: Computed property to get the weighted rating.
    - is_available: Computed property to check if the item is available.
    - is_free: Computed property to check if the item is free.

    Validators:
    - to_datetime: Validator to convert release date to datetime.
    - parse_tags: Validator to parse and filter tags.
    - parse_languages: Validator to parse and filter languages.
    """
    global_average_rating: ClassVar[float] = 0
    vote_confidence: ClassVar[float] = 0

    id: str
    additional_ids: list[str] = []
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
    iarc: Annotated[_IarcRating, Field(
        default=_IarcRating(),
        validation_alias=AliasPath('iarc_cert', 'iarc_rating')
    )]
    platform: str
    internet_connection: str | None
    website: str = Field(validation_alias='website_url')
    app_images: AppImages = AppImages()
    translations: list[Translation] | None = None
    keywords: list[str] = []
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

    def set_additional_details(
        self,
        additionals: AppAdditionalDetails
    ) -> None:
        """
        Method to set additional details from an AppAdditionalDetails instance.

        Args:
        - additionals (AppAdditionalDetails): The AppAdditionalDetails
            instance.
        """
        self.translations = additionals.translations
        self.app_images = additionals.images
        self.keywords = additionals.keywords

    @property
    def resources(self) -> list[AppImage]:
        """
        Property to get a list of AppImage resources.

        Returns:
        - list[AppImage]: The list of AppImage resources.
        """
        def add_images(images: AppImages | None) -> None:
            if images is None:
                return
            res.extend(images.get_images())

        res: list[AppImage] = []
        if self.iarc.iarc_icon:
            res.append(self.iarc.iarc_icon)
        add_images(self.app_images)
        for item in self.translations or []:
            add_images(item.images)
        return res

    @computed_field  # type: ignore[misc]
    @property
    def votes(self) -> int:
        """
        Computed property to get the sum of votes.

        Returns:
        - int: The sum of votes.
        """
        return sum(r.votes for r in self.hist)

    @computed_field  # type: ignore[misc]
    @property
    def rating(self) -> float:
        """
        Computed property to get the average rating.

        Returns:
        - float: The average rating.
        """
        if self.votes == 0:
            return 0
        rating: int = sum(r.votes * r.rating for r in self.hist)
        return round(rating / self.votes, 6)

    @computed_field  # type: ignore[misc]
    @property
    def weighted_rating(self) -> float:
        """
        Computed property to get the weighted rating.

        Returns:
        - float: The weighted rating.
        """
        m: float = Item.global_average_rating
        c: float = Item.vote_confidence
        a: float = max(100, c)
        r: float = self.rating / 5
        v: int = self.votes
        return (m + r * v + m / 5 * a) / (m + c + v + a) * 5

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        """
        Computed property to check if the item is available.

        Returns:
        - bool: True if the item is available, False otherwise.
        """
        return self.price is not None

    @computed_field  # type: ignore[misc]
    @property
    def is_free(self) -> bool:
        """
        Computed property to check if the item is free.

        Returns:
        - bool: True if the item is free, False otherwise.
        """
        return self.price is not None and self.price == 0

    @validator("release_date", pre=True)
    @classmethod
    def to_datetime(cls, val: str | None) -> datetime:
        """
        Validator to convert release date to datetime.

        Args:
        - val (str | None): The input release date string.

        Returns:
        - datetime: The converted datetime value.
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
        Validator to parse and filter tags.

        Args:
        - val (list[dict[str, str]]): The list of tag dictionaries.

        Returns:
        - list[str]: The filtered list of tag names.
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
        Validator to parse and filter supported languages.

        Args:
        - val (list[dict[str, str]]): The list of language dictionaries.

        Returns:
        - list[str]: The filtered list of supported language names.
        """
        return [x['name'] for x in val]


class Error(BaseModel):
    """
    Model for representing errors in Oculus applications.

    Attributes:
    - message (str): The error message.
    - severity (str): The severity of the error.
    - mids (list[str]): List of message IDs.
    - path (list[int | str]): List representing the path of the error.
    """
    message: str
    severity: str
    mids: list[str]
    path: list[int | str]


class OculusApp(BaseModel):
    """
    Model representing the overall details of an Oculus application.

    Attributes:
    - package (str | None): The package name of the application.
    - data (Item): The details of the application.
    - errors (list[Error]): List of errors in the application.
    """
    package: str | None = None
    data: Annotated[Item, Field(validation_alias=AliasPath("data", "item"))]
    errors: list[Error] = []
