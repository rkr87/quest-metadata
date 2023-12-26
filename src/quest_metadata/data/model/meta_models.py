"""
meta_models.py

This module contains the definition of two classes, MetaResource and MetaError,
that represent meta-resources and meta-errors, respectively.

Classes:
    MetaResource: Represents a meta-resource with a root and URL.
    MetaError: Represents a meta-error with message, severity, mids, and path.

"""
from typing import Any

from base.base_model import BaseModel, RootModel


class MetaResource(RootModel[str]):
    """
    Represents a meta-resource with a root and URL.
    """

    root: str
    _url: str

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization method to set _url and modify root.
        """
        self._url = self.root
        self.root = self._url.split('/')[-1].partition("?")[0]
        return super().model_post_init(__context)

    @property
    def url(self) -> str:
        """
        Getter method to retrieve the URL of the meta-resource.

        Returns:
            str: The URL associated with the meta-resource.
        """
        return self._url

    def __str__(self) -> str:
        """
        Returns a string representation of the root identifier.

        Returns:
            str: String representation of the root identifier.
        """
        return self.root


class MetaError(BaseModel):
    """
    Represents a meta-error with message, severity, mids, and path.

    Attributes:
        message (str): The error message.
        severity (str): The severity level of the error.
        mids (list[str]): List of message IDs associated with the error.
        path (list[int | str]): List representing the error path.

    """
    message: str
    severity: str
    mids: list[str]
    path: list[int | str]
