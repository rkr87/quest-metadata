"""
Module providing the `SearchResult` and `StoreSearch` models for store search
results.
"""
from typing import Any

from pydantic import AliasPath, Field, field_validator

from base.models import BaseModel, RootListModel


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

    def fetch_exact_results(self, search_term: str) -> list[SearchResult]:
        """Fetches exact search results based on the provided search term."""
        return [
            r for r in self.root
            if r.display_name.lower() == search_term.lower()
        ]
