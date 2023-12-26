"""
store_section.py

This module contains Pydantic models for representing store-related entities.

Classes:
    StoreLogos: Pydantic model for representing logos in a store.
    StoreSection: Root dictionary model for a store section with logos.
"""
from typing import Any

from pydantic import AliasPath, Field, field_validator

from base.base_model import BaseModel
from base.root_dict_model import RootDictModel
from data.model.meta_models import MetaResource


class StoreLogos(BaseModel):
    """
    Pydantic model for representing logos in a store.
    """
    portrait: MetaResource = \
        Field(validation_alias=AliasPath('cover_portrait_image', 'uri'))
    landscape: MetaResource = \
        Field(validation_alias=AliasPath('cover_landscape_image', 'uri'))
    square: MetaResource = \
        Field(validation_alias=AliasPath('cover_square_image', 'uri'))


class StoreSection(RootDictModel[str, StoreLogos]):
    """
    Root dictionary model for a store section with logos.
    """
    @field_validator("root", mode="before")
    @classmethod
    def flatten(cls, val: dict[str, Any]) -> dict[str, Any]:
        """
        Flatten the provided dictionary representing a store section.

        Args:
            val (dict[str, Any]): The input dictionary.

        Returns:
            dict[str, Any]: The flattened dictionary.
        """
        flatten: list[dict[str, Any]] = \
            val["data"]["node"]["all_items"]["edges"]
        return {n['id']: n for i in flatten if (n := i['node'])}
