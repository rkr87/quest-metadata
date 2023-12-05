"""
Module: meta_parser

The `meta_parser` module contains the `MetaParser` class, which is designed
for parsing and consolidating meta information from a list of `MetaResponse`
objects into a single `MetaResult` object. The class provides methods for
various aspects of the parsing and consolidation process.

Classes:
    MetaParser: A final class for parsing and consolidating meta information.

"""

from typing import Any, Tuple, TypeVar

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.model.meta_response import Item, MetaResponse


@final
class MetaParser(NonInstantiable):
    """
    MetaParser class for parsing and consolidating meta information.

    This class cannot be subclassed, and its primary method is `parse`
    for consolidating MetaResponse objects.
    """
    _launch_method: str = "parse"

    @classmethod
    def parse(cls, meta_responses: list[MetaResponse]) -> MetaResponse:
        """
        Parse and consolidate a list of MetaResponse objects into a
        single MetaResult.

        Args:
            meta_responses (list[MetaResponse]): List of MetaResponse
                objects to be consolidated.

        Returns:
            MetaResult: Consolidated MetaResult object.
        """
        consol: MetaResponse
        if len(meta_responses) == 1:
            consol = meta_responses[0]
        else:
            base: Tuple[MetaResponse, list[MetaResponse]] = cls._identify_base(meta_responses)
            consol = base[0]
            for merge in base[1]:
                cls._consolidate_results(consol.data.root, merge.data.root)
        return consol

    @classmethod
    def _identify_base(
        cls,
        responses: list[MetaResponse]
    ) -> Tuple[MetaResponse, list[MetaResponse]]:
        """
        Identify the base result from a list of MetaResult objects.

        The base result is chosen based on specific criteria.

        Args:
            results (list[MetaResult]): List of MetaResult objects.

        Returns:
            Tuple[MetaResult, list[MetaResult]]: Tuple containing the
                base result and the remaining list of results.
        """
        base_result: Tuple[int, MetaResponse] = 0, responses[0]

        for i, result in enumerate(responses[1:], start=1):
            if cls._new_base_check(base_result[1].data.root, result.data.root):
                base_result = i, result

        base_index, base_response = base_result
        responses.pop(base_index)

        return base_response, responses

    @classmethod
    def _new_base_check(cls, base: Item, new: Item) -> bool:
        """
        Check if a new result should be considered as the base result.

        Criteria include comparing release dates and votes.

        Args:
            base (Item): Base item.
            new (Item): New item to be checked.

        Returns:
            bool: True if the new item should be considered as the base result,
                False otherwise.
        """
        return (
            new.release_date.root > base.release_date.root or
            (
                new.release_date.root == base.release_date.root and
                new.votes > base.votes
            )
        )

    @classmethod
    def _consolidate_results(cls, base: Item, update: Item) -> None:
        """
        Consolidate information from the base and update items.

        Args:
            base (Item): Base item to be updated.
            update (Item): Update item containing additional information.
        """
        lists: list[Tuple[list[Any], list[Any]]] = [
            (base.id.root, update.id.root),
            (base.genres, update.genres),
            (base.input_devices, update.input_devices),
            (base.games_modes, update.games_modes),
            (base.languages, update.languages),
            (base.platforms, update.platforms),
            (base.player_modes, update.player_modes),
            (base.tags.root, update.tags.root),
            (base.screenshots, update.screenshots),
        ]

        for base_list, update_list in lists:
            cls._update_list(base_list, update_list)

        for item in update.hist:
            for base_item in base.hist:
                if base_item.rating == item.rating:
                    base_item.votes += item.votes
                    break

    _KT = TypeVar("_KT")

    @classmethod
    def _update_list(
        cls,
        base: list[_KT] | None,
        update: list[_KT] | None
    ) -> None:
        """
        Update a list, ensuring no duplicate items are added.

        Args:
            base (list[str] | None): Base list to be updated.
            update (list[str] | None): Update list containing additional items.
        """
        if update is not None:
            if base is None:
                base = update
            else:
                base.extend(item for item in update if item not in base)
