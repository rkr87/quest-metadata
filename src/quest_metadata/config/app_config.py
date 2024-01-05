"""
Module providing the application configuration model.

This module defines the `AppConfig` class, a singleton configuration model for
the application.

Classes:
- AppConfig: Singleton configuration model for the application.

Usage:
```python

app_config = AppConfig()
print(app_config.scrape_locale) > "en_US"
app_config.scrape_locale = "fr_FR"
"""
import json
from typing import Any, Self

from aiofiles import open as aopen
from aiofiles.os import path
from pydantic import Field
from pydantic.v1.utils import deep_update

from base.models import BaseModel, SingletonModel

CONFIG_FILE = ".config/app/app_config.json"


class ImageProps(BaseModel):
    """Model representing properties of an image."""
    max_width: int | None = None
    max_height: int | None = None
    min_height: int | None = None
    min_width: int | None = None
    crop_height: int | None = None
    crop_width: int | None = None


COVER_DEF = ImageProps(max_height=300)
ICON_DEF = ImageProps(
    max_width=64,
    max_height=64,
    min_height=64,
    min_width=64,
    crop_height=64,
    crop_width=64
)
LOGO_DEF = ImageProps(max_width=800, max_height=240, min_height=60)
BANNER_DEF = ImageProps(
    max_width=1600,
    min_height=480,
    crop_height=480,
    crop_width=1600
)


class _Image(BaseModel):
    """Model representing the definition of an image."""
    include: bool = False
    properties: ImageProps = ImageProps()


class _Images(BaseModel):
    """Model representing config options for various image types."""
    cover_landscape: _Image = _Image(include=True, properties=COVER_DEF)
    cover_portrait: _Image = _Image(include=True, properties=COVER_DEF)
    cover_square: _Image = _Image(include=True, properties=COVER_DEF)
    hero: _Image = _Image(include=True, properties=BANNER_DEF)
    icon: _Image = _Image(include=True, properties=ICON_DEF)
    immersive_layer_backdrop: _Image = \
        _Image(include=True, properties=BANNER_DEF)
    immersive_layer_logo: _Image = _Image(include=True, properties=LOGO_DEF)
    logo_transparent: _Image = _Image(include=True, properties=LOGO_DEF)
    small_landscape: _Image = _Image()
    cubemap_source: _Image = _Image()
    immersive_layer_object_left: _Image = _Image()
    immersive_layer_object_right: _Image = _Image()

    def image_type_defined(self, image_type: str) -> bool:
        """Check if the image type is defined."""
        return hasattr(self, image_type)

    def _get(self, image_type: str) -> _Image:
        """Get the image definition."""
        return getattr(self, image_type, _Image())

    def include_image(self, image_type: str) -> bool:
        """Check if the image should be included in parsing."""
        return self._get(image_type).include

    def get_properties(self, image_type: str) -> ImageProps:
        """Get the properties of the image."""
        return self._get(image_type).properties


class AppConfig(SingletonModel):
    """
    Singleton configuration model for the application.
    """
    logging_config: str = ".config/app/logging.conf"
    scrape_locale: str = "en_US"
    data_path: str = ".data"
    apps_filename: str = "_apps.json"
    resource_path: str = ".res"
    error_path: str = ".errors"
    error_log_retention: int = 7
    constructed: bool = Field(default=False, exclude=True)
    include_binaries: list[str] = ["AndroidBinary"]
    images: _Images = _Images()
    max_threads: int | None = None

    @classmethod
    async def load_config(cls, override_file: str | None = None) -> Self:
        """
        Load configuration from file.

        Args:
        - override_file (Optional[str]): Path to an override configuration
            file.

        Returns:
        - AppConfig: The loaded configuration model.
        """
        data: dict[str, str | bool] = {"constructed": True}
        if await path.exists(CONFIG_FILE):
            async with aopen(CONFIG_FILE, "r", encoding="utf8") as config:
                data.update(json.loads(await config.read()))
        if override_file and await path.exists(override_file):
            async with aopen(override_file, "r", encoding="utf8") as override:
                data = deep_update(data, json.loads(await override.read()))
        model: Self = cls.model_validate(data)
        cls.add_instance(model)
        return model

    @classmethod
    async def save_defaults(cls) -> None:
        """
        Save default configuration to file.
        """
        data: dict[str, str | bool] = {"constructed": True}
        model: AppConfig = cls.model_validate(data)
        await model.save_json(CONFIG_FILE)

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization hook for the model.

        Args:
        - __context (Any): The context of the model post-initialization.
        """
        if self.constructed:
            return super().model_post_init(__context)
        raise TypeError(
            "Config hasn't been loaded. " +
            "Ensure you've run AppConfig.load_config()"
        )
