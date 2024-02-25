"""
Module providing models for application images, translations,
and additional details.

Classes:
- AppImage: Model for representing an application image.
- AppImages: Model for a collection of application images.
- Translation: Model for representing translation details.
- AppAdditionalDetails: Model for additional details of an application.
"""
from logging import Logger, getLogger
from typing import Any

from pydantic import (AliasPath, Field, field_validator, model_serializer,
                      model_validator)

from base.models import BaseModel, RootDictModel
from config.app_config import AppConfig, ImageProps
from helpers.dict import get_nested_keys
from utils.error_manager import ErrorManager


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


class AppImages(RootDictModel[str, AppImage | None]):
    """
    Model for a collection of application images.
    """

    def get_images(self) -> list[AppImage]:
        """
        Gets a list of all non-None images.

        Returns:
        - list[AppImage]: The list of non-None images.
        """
        images: list[AppImage] = []
        for x in self.values():
            if isinstance(x, AppImage):
                images.append(x)
        return images

    def get_serialised_object(self) -> dict[str, str | None]:
        """create an object matching serialized output"""
        output: dict[str, str | None] = {}
        for k, v in self.root.items():
            output[k] = v if v is None else v.serialize()
        return output

    @field_validator("root", mode="before")
    @classmethod
    def _list_to_dict(
        cls,
        val: list[dict[str, Any]]
    ) -> dict[str, AppImage | None]:
        """
        Class method to convert a list of dictionaries to a dictionary.

        Args:
        - val (list[dict[str, Any]]): The input list of dictionaries.

        Returns:
        - dict[str, Any]: The converted dictionary.
        """
        base: dict[str, AppImage | None] = {
            x: None
            for x in AppConfig().images.model_fields
            if AppConfig().images.include_image(x)
        }
        base.update({
            x.type: x
            for y in val
            if (x := cls._get_image_props(y)) is not None
        })
        return base

    @classmethod
    def _get_image_props(
        cls,
        val_dict: dict[str, str]
    ) -> AppImage | None:
        """
        Get the application image properties based on the provided dictionary.

        Args:
        - val_dict (dict[str, str]): The dictionary containing image details.

        Returns:
        - AppImage | None: An instance of AppImage if properties are valid,
            else None.
        """
        if not (image := cls._parse_image_type(val_dict)):
            return None
        if AppConfig().images.include_image(image):
            return AppImage.model_validate({
                'uri': val_dict['uri'],
                'props': AppConfig().images.get_properties(image),
                'type': image
            })
        if AppConfig().images.image_type_defined(image):
            return None
        error: str = ErrorManager().capture(
            "ImageTypeNotFound",
            "Getting config information for image type",
            f"Image Type not defined in config: {image}",
            {
                "ImageType": image
            }
        )
        logger: Logger = getLogger(__name__)
        logger.warning(error)
        return None

    @classmethod
    def _parse_image_type(cls, val_dict: dict[str, str]) -> str | None:
        """
        Parse the image type from the provided dictionary.

        Args:
        - val_dict (dict[str, str]): The dictionary containing image details.

        Returns:
        - str | None: The parsed image type if successful, else None.
        """
        try:
            return val_dict['image_type'].replace("APP_IMG_", "").lower()
        except TypeError as e:
            error = ErrorManager().capture(
                e,
                "Getting image type from app response",
                "Unable to parse image type string",
                {
                    "item": val_dict
                }
            )
            logger: Logger = getLogger(__name__)
            logger.warning(error)
            return None


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
