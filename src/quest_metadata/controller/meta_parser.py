"""
Module: meta_parser

The `meta_parser` module contains the `MetaParser` class, which is designed
for parsing and consolidating meta information from a list of `MetaResponse`
objects into a single `MetaResult` object. The class provides methods for
various aspects of the parsing and consolidation process.

Classes:
    MetaParser: A final class for parsing and consolidating meta information.

"""
from typing import Tuple

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.model.meta_response import MetaResponse
from data.model.meta_result import Item, MetaResult


@final
class MetaParser(NonInstantiable):
    """
    MetaParser class for parsing and consolidating meta information.

    This class cannot be subclassed, and its primary method is `parse`
    for consolidating MetaResponse objects.
    """
    _launch_method: str = "parse"

    @classmethod
    def parse(cls, meta_responses: list[MetaResponse]) -> MetaResult:
        """
        Parse and consolidate a list of MetaResponse objects into a
        single MetaResult.

        Args:
            meta_responses (list[MetaResponse]): List of MetaResponse
                objects to be consolidated.

        Returns:
            MetaResult: Consolidated MetaResult object.
        """
        results: list[MetaResult] = cls._convert(meta_responses)
        consol: MetaResult
        if len(results) == 1:
            consol = results[0]
        else:
            base: Tuple[MetaResult, list[MetaResult]] = cls._identify_base(results)
            consol = base[0]
            for merge in base[1]:
                cls._consolidate_results(consol.data, merge.data)
        cls._calc_weighted_ratings(consol.data)
        return consol

    @classmethod
    def _convert(cls, responses: list[MetaResponse]) -> list[MetaResult]:
        """
        Convert a list of MetaResponse objects to a list of MetaResult objects.

        Args:
            responses (list[MetaResponse]): List of MetaResponse objects to
                be converted.

        Returns:
            list[MetaResult]: List of converted MetaResult objects.
        """
        return [MetaResult(**r.model_dump()) for r in responses]

    @classmethod
    def _identify_base(
        cls,
        results: list[MetaResult]
    ) -> Tuple[MetaResult, list[MetaResult]]:
        """
        Identify the base result from a list of MetaResult objects.

        The base result is chosen based on specific criteria.

        Args:
            results (list[MetaResult]): List of MetaResult objects.

        Returns:
            Tuple[MetaResult, list[MetaResult]]: Tuple containing the
                base result and the remaining list of results.
        """
        base_result: Tuple[int, MetaResult] = 0, results[0]
        for index, result in enumerate(results, 1):
            if cls._new_base_check(base_result[1].data, result.data):
                base_result = index - 1, result
        results.pop(base_result[0])
        return base_result[1], results

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
            new.release_date > base.release_date or
            (
                new.release_date == base.release_date and
                (new.votes or 0) > (base.votes or 0)
            )
        )

    @classmethod
    def _calc_weighted_ratings(cls, consol: Item) -> None:
        """
        Calculate weighted ratings based on votes and rating values.

        Args:
            consol (Item): Item containing information to calculate
                weighted ratings.
        """
        votes: int = sum(r.votes for r in consol.hist)
        rating: int = sum(r.votes * r.rating for r in consol.hist)
        if votes != 0:
            consol.rating = rating / votes
            consol.votes = votes

    @classmethod
    def _consolidate_results(cls, base: Item, update: Item) -> None:
        """
        Consolidate information from the base and update items.

        Args:
            base (Item): Base item to be updated.
            update (Item): Update item containing additional information.
        """
        lists: list[Tuple[list[str], list[str]]] = [
            (base.id, update.id),
            (base.genres, update.genres),
            (base.input_devices, update.input_devices),
            (base.games_modes, update.games_modes),
            (base.languages, update.languages),
            (base.platforms, update.platforms),
            (base.player_modes, update.player_modes),
            (base.tags, update.tags),
            (base.screenshots, update.screenshots),
        ]
        for base_list, update_list in lists:
            cls._update_list(base_list, update_list)

        for item in update.hist:
            for base_item in base.hist:
                if base_item.rating == item.rating:
                    base_item.votes += item.votes
                    break

    @classmethod
    def _update_list(
        cls,
        base: list[str] | None,
        update: list[str] | None
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
