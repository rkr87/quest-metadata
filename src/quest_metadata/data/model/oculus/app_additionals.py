"""
Module providing models for application images, translations,
and additional details.

Classes:
- AppImage: Model for representing an application image.
- AppImages: Model for a collection of application images.
- Translation: Model for representing translation details.
- AppAdditionalDetails: Model for additional details of an application.
"""
from typing import Any

from pydantic import AliasPath, Field, model_serializer, model_validator

from base.models import BaseModel
from config.app_config import AppConfig
from controller.image_manager import ImageProps
from utils.dict import get_nested_keys

IMG_TYPES: dict[str, ImageProps] = {
    "COVER_LANDSCAPE": ImageProps(max_height=300),
    "COVER_PORTRAIT": ImageProps(max_height=300),
    "COVER_SQUARE": ImageProps(max_height=300),
    "ICON": ImageProps(max_width=64, max_height=64),
    "HERO": ImageProps(
        max_width=1600,
        min_height=480,
        crop_height=480,
        crop_width=1600
    ),
    "IMMERSIVE_LAYER_BACKDROP": ImageProps(
        max_width=1600,
        min_height=480,
        crop_height=480,
        crop_width=1600
    ),
    "LOGO_TRANSPARENT": ImageProps(
        max_width=800,
        max_height=240,
        min_height=60
    ),
    "IMMERSIVE_LAYER_LOGO": ImageProps(
        max_width=800,
        max_height=240,
        min_height=60
    )
}


class AppImage(BaseModel):
    """
    Model for representing an application image.

    Attributes:
    - name (str): The name of the application image.
    - url (str): The URL of the application image.
    - props (ImageProps): Properties of the application image.
    - type (str): The type of the application image.

    Methods:
    - serialize: Serializes the model to its name.
    - set_vals: Class method to set values, extracting the name from the URI.
    """
    name: str
    url: str = Field(validation_alias='uri')
    props: ImageProps
    type: str
    data: bytes | None = None

    @model_serializer
    def serialize(self) -> str:
        """
        Serializes the model to its name.

        Returns:
        - str: The name of the application image.
        """
        return self.name

    @model_validator(mode="before")
    @classmethod
    def set_vals(cls, val: dict[str, Any]) -> dict[str, Any]:
        """
        Class method to set values, extracting the name from the URI.

        Args:
        - val (dict[str, Any]): The input dictionary with values.

        Returns:
        - dict[str, Any]: The modified dictionary with the name extracted.
        """
        val['name'] = val['uri'].split('/')[-1].partition("?")[0]
        if val.get('props') is None:
            val['props'] = ImageProps()
        return val


class AppImages(BaseModel):
    """
    Model for a collection of application images.

    Attributes:
    - cover_landscape (AppImage | None): The cover landscape image.
    - cover_portrait (AppImage | None): The cover portrait image.
    - cover_square (AppImage | None): The cover square image.
    - hero (AppImage | None): The hero image.
    - iarc_icon (AppImage | None): The IARC icon image.
    - icon (AppImage | None): The icon image.
    - immersive_layer_backdrop (AppImage | None): The immersive layer
        backdrop image.
    - immersive_layer_logo (AppImage | None): The immersive layer logo image.
    - logo_transparent (AppImage | None): The logo transparent image.

    Methods:
    - get_images: Gets a list of all non-None images.
    - list_to_dict: Class method to convert a list of dictionaries to a
        dictionary.
    """
    cover_landscape: AppImage | None = None
    cover_portrait: AppImage | None = None
    cover_square: AppImage | None = None
    hero: AppImage | None = None
    iarc_icon: AppImage | None = None
    icon: AppImage | None = None
    immersive_layer_backdrop: AppImage | None = None
    immersive_layer_logo: AppImage | None = None
    logo_transparent: AppImage | None = None

    def get_images(self) -> list[AppImage]:
        """
        Gets a list of all non-None images.

        Returns:
        - list[AppImage]: The list of non-None images.
        """
        images: list[AppImage] = []
        for _, x in iter(self):
            if isinstance(x, AppImage):
                images.append(x)
        return images

    @model_validator(mode="before")
    @classmethod
    def list_to_dict(cls, val: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Class method to convert a list of dictionaries to a dictionary.

        Args:
        - val (list[dict[str, Any]]): The input list of dictionaries.

        Returns:
        - dict[str, Any]: The converted dictionary.
        """
        return {
            x.lower(): {
                'uri': i['uri'],
                'props': IMG_TYPES.get(x),
                'type': x.lower()
            }
            for i in val
            if (x := i['image_type'].replace("APP_IMG_", ""))
            and x in IMG_TYPES
        }


class Translation(BaseModel):
    """
    Model for representing translation details.

    Attributes:
    - images (AppImages): The collection of application images.
    - locale (str): The locale of the translation.
    - display_name (str): The display name of the translation.
    - keywords (list[str]): The keywords of the translation.
    - long_description (str): The long description of the translation.
    - long_description_uses_markdown (bool): Indicates if the long description
      uses Markdown.
    - short_description (str): The short description of the translation.
    """
    images: AppImages = Field(
        validation_alias=AliasPath(
            "imagesExcludingScreenshotsAndMarkdown", "nodes"
        ),
        default=AppImages()
    )
    locale: str
    display_name: str
    keywords: list[str] = []
    long_description: str
    long_description_uses_markdown: bool
    short_description: str


class AppAdditionalDetails(BaseModel):
    """
    Model for additional details of an application.

    Attributes:
    - translations (list[Translation]): The list of translation details.
    - images (AppImages): The collection of application images.
    - keywords (list[str]): The list of keywords.
    """
    translations: list[Translation] = []
    images: AppImages = AppImages()
    keywords: list[str] = []

    @model_validator(mode="before")
    @classmethod
    def flatten(cls, val: dict[str, Any]) -> dict[str, Any] | None:
        """
        Class method to flatten a nested dictionary structure.

        Args:
        - val (dict[str, Any]): The input dictionary.

        Returns:
        - dict[str, Any] | None: The flattened dictionary or None if empty.
        """
        key_path: list[str | int | list[str]] = [
            "data", "node", ["lastRevision", "firstRevision"], "nodes", 0,
            "pdp_metadata", "translations", "nodes"
        ]
        flatten: list[dict[str, Any]] | None = get_nested_keys(val, key_path)
        if flatten is None or len(flatten) == 0:
            return None
        loc = next((
            item for item in flatten
            if item['locale'] == AppConfig().scrape_locale or len(flatten) == 1
        ))
        to_dict: dict[str, Any] = {
            "images": loc["imagesExcludingScreenshotsAndMarkdown"]["nodes"],
            "keywords": loc['keywords']
        }
        to_dict["translations"] = [item for item in flatten if item != loc]
        return to_dict
