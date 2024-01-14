"""
Module providing the `SearchResult` and `StoreSearch` models for store search
results.
"""
from typing import Any

from pydantic import AliasPath, Field, field_validator

from base.models import BaseModel, RootListModel
from helpers.string import normalised_compare


class SearchResult(BaseModel):
    """
    Model representing a search result.

    Attributes:
    - display_name (str): The display name of the search result.
    - id (str): The ID of the search result.
    """
    display_name: str = \
        Field(validation_alias=AliasPath("target_object", "display_name"))
    id: str = \
        Field(validation_alias=AliasPath("target_object", "id"))
    is_concept: bool = \
        Field(validation_alias=AliasPath("target_object", "is_concept"))


class StoreSearch(RootListModel[SearchResult]):
    """
    List-based model for a collection of store search results.
    """
    @field_validator("root", mode="before")
    @classmethod
    def flatten(cls, val: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Flattens a dictionary structure to a list of store search result nodes.
        """
        flatten: list[dict[str, Any]] = \
            val["data"]["viewer"]["contextual_search"]["all_category_results"]

        output: list[dict[str, Any]] = []
        for i in flatten:
            output.extend(i['search_results']['nodes'])
        return output

    def filter_results(
        self,
        search_term: str,
        include_all_applab: bool = False
    ) -> list[SearchResult]:
        """Fetches exact search results based on the provided search term."""

        noise: list[str] = ["VR", "MR-Fix", "Multi-Install"]

        return [
            r for r in self.root
            if (
                normalised_compare(r.display_name, search_term, noise) or
                (r.is_concept and include_all_applab)
            )
        ]
