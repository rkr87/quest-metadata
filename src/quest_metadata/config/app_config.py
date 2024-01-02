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

from base.models import SingletonModel

CONFIG_FILE = ".config_app/app_config.json"


class AppConfig(SingletonModel):
    """
    Singleton configuration model for the application.
    """
    logging_config: str = ".config_app/logging.conf"
    scrape_locale: str = "en_US"
    data_path: str = ".data"
    resource_path: str = ".res"
    constructed: bool = Field(default=False, exclude=True)

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
                deep_update(data, json.loads(await override.read()))
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
