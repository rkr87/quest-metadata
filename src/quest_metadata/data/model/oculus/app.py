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
from math import floor
from typing import Annotated, Any, ClassVar

from pydantic import (AliasPath, Field, computed_field, field_validator,
                      model_validator, validator)

from base.models import BaseModel
from data.model.local.processed_app import ProcessedApp
from data.model.oculus.app_additionals import (AppAdditionalDetails, AppImage,
                                               AppImages)
from data.model.oculus.app_changelog import AppChangeEntry
from utils.constants import (GENRE_MAPPING, MODE_MAPPING, TAG_MAPPING,
                             TAG_TRENDING)
from utils.error_manager import ErrorManager


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


class Item(BaseModel):  # pylint: disable=R0902,R0904
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
    # name: str = Field(validation_alias='display_name')
    app_name: str = Field(validation_alias='appName')
    # type_name: str = Field(validation_alias='__typename')
    # appstore_type: str = Field(validation_alias='__isAppStoreItem')
    category_id: Annotated[
        str | None,
        Field(default=None, validation_alias='category', exclude=True)
    ]
    category_name: Annotated[str | None, Field(default=None, exclude=True)]
    release_date: str = Field(
        default="1980-01-01T00:00:00.000Z",
        validation_alias=AliasPath('release_info', 'display_date')
    )
    description: str = Field(validation_alias='display_long_description')
    # markdown: bool = Field(validation_alias='long_description_uses_markdown')
    developer: str = Field(validation_alias='developer_name')
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
    # age_rating: str | None = Field(
    #     default=None,
    #     validation_alias=AliasPath('age_rating', 'category_name')
    # )
    iarc: Annotated[_IarcRating, Field(
        default=_IarcRating(),
        validation_alias=AliasPath('iarc_cert', 'iarc_rating')
    )]
    # platform: str
    internet_connection: str
    website: str = Field(validation_alias='website_url')
    app_images: AppImages = AppImages()
    # translations: list[Translation] | None = None
    changelog: list[AppChangeEntry] = []

    # has_ads: bool = Field(validation_alias='has_in_app_ads')
    # sensor_req: bool = Field(validation_alias='is_360_sensor_setup_required')
    price: int | None = Field(
        default=None,
        validation_alias=AliasPath("current_offer", "price", "offset_amount"),
        exclude=True
    )
    is_demo_of: str | None = Field(
        default=None,
        validation_alias=AliasPath("is_demo_of", "id"),
        exclude=True
    )
    on_rookie: bool = False
    app_additionals: Annotated[
        AppAdditionalDetails | None,
        Field(
            default=None,
            exclude=True
        )
    ]

    @computed_field  # type: ignore[misc]
    @property
    def keywords(self) -> list[str]:
        """get stem parent"""
        if self.app_additionals is None:
            return []
        return self.app_additionals.get_keywords()

    @computed_field  # type: ignore[misc]
    @property
    def last_update(self) -> int:
        """field representing most recent update"""
        return max(
            [
                self.general_update,
                self.genre_update,
                self.device_update,
                self.mode_update,
                self.language_update,
                self.platform_update,
                self.player_mode_update,
                self.keyword_update,
                self.tag_update,
                self.rating_update,
                self.iarc_detail_update,
                self.changelog_update
            ]
        )

    general_update: int = 475000
    genre_update: int = 475000
    device_update: int = 475000
    mode_update: int = 475000
    language_update: int = 475000
    platform_update: int = 475000
    player_mode_update: int = 475000
    changelog_update: int = 475000
    keyword_update: int = 475000
    tag_update: int = 475000
    rating_update: int = 475000
    iarc_detail_update: int = 475000

    def set_update_details(
        self,
        new_date: int,
        prev_app: ProcessedApp | None = None
    ) -> None:
        """
        Method to determine last date of change for various data elements.
        """
        if prev_app is None:
            self.general_update = new_date
            self.genre_update = new_date
            self.device_update = new_date
            self.mode_update = new_date
            self.language_update = new_date
            self.platform_update = new_date
            self.player_mode_update = new_date
            self.keyword_update = new_date
            self.tag_update = new_date
            self.rating_update = new_date
            self.iarc_detail_update = new_date
            self.changelog_update = new_date
            return
        self.general_update = self._get_general_update(new_date, prev_app)
        self.rating_update = self._get_rating_update(new_date, prev_app)
        self.iarc_detail_update = self._get_iarc_detail_update(
            new_date,
            prev_app
        )
        self.changelog_update = self._get_changelog_update(new_date, prev_app)
        self._check_details_update(new_date, prev_app)

    def _get_general_update(
        self,
        new_date: int,
        prev_app: ProcessedApp
    ) -> int:
        """determine if previous update date should be used"""
        if (
            self.app_name != prev_app.app_name or  # pylint: disable=R0916
            self.release_date != prev_app.release_date or
            self.description != prev_app.description or
            self.developer != prev_app.developer or
            self.publisher != prev_app.publisher or
            self.comfort != prev_app.comfort or
            self.internet_connection != prev_app.internet_connection or
            self.website != prev_app.website or
            self.on_rookie != prev_app.on_rookie or
            self.category != prev_app.category or
            self.weighted_rating != prev_app.weighted_rating or
            self.app_images.get_serialised_object() != prev_app.app_images
        ):
            return new_date
        return prev_app.general_update

    def _get_rating_update(
        self,
        new_date: int,
        prev_app: ProcessedApp
    ) -> int:
        """determine if previous update date should be used"""
        if (self.votes != prev_app.votes or self.rating != prev_app.rating):
            return new_date
        return prev_app.rating_update

    def _get_iarc_detail_update(
        self,
        new_date: int,
        prev_app: ProcessedApp
    ) -> int:
        """determine if previous update date should be used"""
        if (
            self.iarc.descriptors != prev_app.iarc.descriptors or
            self.iarc.elements != prev_app.iarc.elements
        ):
            return new_date
        return prev_app.iarc_detail_update

    def _get_changelog_update(
        self,
        new_date: int,
        prev_app: ProcessedApp
    ) -> int:
        """determine if previous update date should be used"""
        new: list[str] = [x.model_dump_json() for x in self.changelog]
        prev: list[str] = [x.model_dump_json() for x in prev_app.changelog]
        if new != prev:
            return new_date
        return prev_app.changelog_update

    def _check_details_update(self,
                              new_date: int,
                              prev_app: ProcessedApp
                              ) -> None:
        """determine if previous update date should be used"""
        self.genre_update = self._prev_list_update(
            prev_app.genres, self.genres, prev_app.genre_update) or new_date
        self.device_update = self._prev_list_update(
            prev_app.devices, self.devices, prev_app.device_update) or new_date
        self.mode_update = self._prev_list_update(
            prev_app.modes, self.modes, prev_app.mode_update) or new_date
        self.language_update = self._prev_list_update(
            prev_app.languages, self.languages, prev_app.language_update
        ) or new_date
        self.platform_update = self._prev_list_update(
            prev_app.platforms, self.platforms, prev_app.platform_update
        ) or new_date
        self.player_mode_update = self._prev_list_update(
            prev_app.player_modes,
            self.player_modes,
            prev_app.player_mode_update
        ) or new_date
        self.keyword_update = self._prev_list_update(
            prev_app.keywords, self.keywords, prev_app.keyword_update
        ) or new_date
        self.tag_update = self._prev_list_update(
            prev_app.tags, self.tags, prev_app.tag_update
        ) or new_date

    # def _get_changelog_update(
    #     self,
    #     new_date: datetime,
    #     prev_app: ProcessedApp
    # ) -> datetime:
    #     """determine if previous update date should be used"""
    #     curr: int = max(x.code for x in self.changelog)
    #     prev: int = max(x.code for x in prev_app.changelog)
    #     if curr > prev:
    #         return new_date
    #     return prev_app.changelog_update

    @staticmethod
    def _prev_list_update(
        list_1: list[str],
        list_2: list[str],
        prev_date: int
    ) -> int | None:
        """determine if previous update date should be used"""
        if set(list_1) == set(list_2):
            return prev_date
        return None

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
        # self.translations = additionals.translations
        self.app_images = additionals.images
        self.app_additionals = additionals

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
        # for item in self.translations or []:
        #     add_images(item.images)
        return res

    @computed_field  # type: ignore[misc]
    @property
    def category(self) -> str:
        """
        Computed category
        """
        return (
            self.category_id or self.category_name or "NOT_SPECIFIED"
        ).upper()

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
        r: float = self.rating / 5
        v: int = self.votes
        return floor((m + r * v + m / 5 * c) / (m + 2 + v + c) * 5 * 10) / 10

    # @computed_field  # type: ignore[misc]
    # @property
    def is_available(self) -> bool:
        """
        Computed property to check if the item is available.

        Returns:
        - bool: True if the item is available, False otherwise.
        """
        return self.price is not None

    # @computed_field  # type: ignore[misc]
    # @property
    def is_free(self) -> bool:
        """
        Computed property to check if the item is free.

        Returns:
        - bool: True if the item is free, False otherwise.
        """
        return self.price is not None and self.price == 0

    @validator(
        "developer",
        "internet_connection",
        "publisher",
        "comfort",
        "website",
        pre=True
    )
    @classmethod
    def set_not_specified(cls, val: str | None) -> str:
        """
        Validator to convert null strings
        """
        return val or "NOT_SPECIFIED"

    @validator("genres", pre=True)
    @classmethod
    def genre_cleanup(cls, val: list[str]) -> list[str]:
        """
        Validator to clean_up genres
        """
        output: list[str] = []
        for v in val:
            if v in GENRE_MAPPING and (x := GENRE_MAPPING[v]) not in output:
                output.append(x)
        return output

    @validator("modes", pre=True)
    @classmethod
    def mode_cleanup(cls, val: list[str]) -> list[str]:
        """
        Validator to clean_up modes
        """
        return [x for x in val if x in MODE_MAPPING]

    @validator("release_date", pre=True)
    @classmethod
    def to_datetime(cls, val: str | None) -> str:
        """
        Validator to convert release date to datetime.

        Args:
        - val (str | None): The input release date string.

        Returns:
        - datetime: The converted datetime value.
        """
        default = "1980-01-01T00:00:00.000Z"
        if val is None:
            return default

        date_formats: list[str] = [
            "%d %b %Y",
            "%b %d, %Y",
            "%b %Y"
        ]
        for fmt in date_formats:
            try:
                date_val: datetime = datetime.strptime(val, fmt)
                return f"{date_val.isoformat(timespec="milliseconds")}Z"
            except ValueError:
                pass
        logger: Logger = getLogger(__name__)
        error: str = ErrorManager().capture(
            "ValueError",
            "Parsing app release date",
            f"Unable to parse date: {val}"
        )
        logger.warning("%s", error)
        return default

    @validator("tags", pre=True)
    @classmethod
    def tag_cleanup(cls, val: list[dict[str, str]]) -> list[str]:
        """
        Validator to clean_up tags
        """
        output: list[str] = []
        key = 'display_name'
        for v in val:
            if (
                (z := v[key]) in TAG_MAPPING and
                (x := TAG_MAPPING[z]) not in output
            ):
                output.append(x)
            if TAG_TRENDING in z.lower() and (y := "Trending") not in output:
                output.append(y)
        return output

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
    - data (Item): The details of the application.
    - errors (list[Error]): List of errors in the application.
    """
    data: Annotated[Item, Field(validation_alias=AliasPath("data", "item"))]
    errors: list[Error] = []


class OculusApps(BaseModel):
    """
    Model representing a list of Oculus application.
    """
    data: list[OculusApp]
