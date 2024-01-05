"""
Module providing a model for application packages.

Classes:
- AppPackage: Model for representing an application package.
"""
from pydantic import AliasPath, Field

from base.models import BaseModel


class AppPackage(BaseModel):
    """
    Model for representing an application package.

    Attributes:
    - name (str | None): The name of the application package.
    """
    name: str | None = Field(default=None, validation_alias=AliasPath(
        "data", "app_binary_info", "info", 0, 'binary', 'package_name'
    ))
