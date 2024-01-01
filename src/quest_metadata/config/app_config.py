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
from base.models import SingletonModel


class AppConfig(SingletonModel):
    """
    Singleton configuration model for the application.
    """
    logging_config: str = ".config_app/logging.conf"
    scrape_locale: str = "en_US"
    data_path: str = ".data"
    resource_path: str = ".res"
