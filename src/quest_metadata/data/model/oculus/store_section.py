"""
Module providing models for store entries and sections.

Classes:
- StoreEntry: Model for representing a store entry.
- StoreSection: List-based model for a collection of store entries.
"""
from typing import Any

from pydantic import field_validator

from base.models import BaseModel, RootListModel


class StoreEntry(BaseModel):
    """
    Model for representing a store entry.

    Attributes:
    - display_name (str): The display name of the store entry.
    - id (str): The identifier for the store entry.
    """
    display_name: str
    id: str


class StoreSection(RootListModel[StoreEntry]):
    """
    List-based model for a collection of store entries.

    Inherits from:
    - RootListModel[StoreEntry]
    """
    @field_validator("root", mode="before")
    @classmethod
    def flatten(cls, val: dict[str, Any]) -> list[str]:
        """
        Flattens a dictionary structure to a list of store entry nodes.

        Args:
        - val (dict[str, Any]): The input dictionary containing store
            entry nodes.

        Returns:
        - list[str]: The flattened list of store entry nodes.
        """
        flatten: list[dict[str, Any]] = \
            val["data"]["node"]["all_items"]["edges"]
        return [i['node'] for i in flatten]
