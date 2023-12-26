"""
Module: meta_parser

The `meta_parser` module contains the `MetaParser` class, which is designed
for parsing and consolidating meta information from a list of `MetaResponse`
objects into a single `MetaResult` object. The class provides methods for
various aspects of the parsing and consolidation process.

Classes:
    MetaParser: A final class for parsing and consolidating meta information.

"""

from logging import Logger, getLogger
from typing import TypeVar

from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.model.meta_app import Item, MetaApp, RatingHist


@final
class MetaParser(NonInstantiable):
    """
    MetaParser class for parsing and consolidating meta information.

    This class cannot be subclassed, and its primary method is `parse`
    for consolidating MetaResponse objects.
    """
    _launch_method: str = "parse"

    @classmethod
    def parse(
        cls,
        meta_responses: list[MetaApp],
        package: str
    ) -> MetaApp:
        """
        Parse and consolidate meta information from a list of MetaResponse
        objects into a single MetaResponse object.

        This method takes a list of MetaResponse objects and consolidates
        them into a single MetaResponse object. The consolidation process
        involves identifying a base result from the list, merging additional
        information from other results into the base, and updating global
        rating statistics.

        Args:
            meta_responses (list[MetaResponse]): List of MetaResponse objects
                to be consolidated.
            package (str): Package identifier.

        Returns:
            MetaResponse: Consolidated MetaResponse object.
        """
        consol: MetaApp = meta_responses[0]
        if len(meta_responses) > 1:
            base: tuple[MetaApp, list[MetaApp]] = cls._identify_base(
                meta_responses
            )
            consol = base[0]
            for merge in base[1]:
                cls._consolidate_results(consol.data, merge.data)
        cls._handle_errors(consol, package)
        consol.package = package
        return consol

    @classmethod
    def _handle_errors(cls, response: MetaApp, package: str) -> None:
        """
        Handle errors in the consolidated MetaResponse.

        Args:
            response (MetaResponse): Consolidated MetaResponse object.
            package (str): Package identifier.
        """
        if response.errors is None or len(response.errors) == 0:
            return
        logger: Logger = getLogger(__name__)
        logger.info("Result contains errors: %s", package)
        for error in response.errors:
            logger.info("%s", error.model_dump_json(
                indent=4,
                exclude_unset=True,
                exclude_none=True)
            )

    @classmethod
    def _identify_base(
        cls,
        responses: list[MetaApp]
    ) -> tuple[MetaApp, list[MetaApp]]:
        """
        Identify the base result from a list of MetaResponse objects.

        The base result is chosen based on specific criteria.

        Args:
            responses (list[MetaResponse]): List of MetaResponse objects.

        Returns:
            Tuple[MetaResponse, list[MetaResponse]]: Tuple containing the
                base result and the remaining list of results.

        This method iterates through the provided list of MetaResponse objects
        and identifies the base result based on specific criteria. The criteria
        are implemented in the `_new_base_check` method. The identified base
        result is removed from the list of responses, and the tuple containing
        the base result and the updated list of responses is returned.
        """
        base_result: tuple[int, MetaApp] = 0, responses[0]

        for i, result in enumerate(responses[1:], start=1):
            if cls._new_base_check(base_result[1].data, result.data):
                base_result = i, result

        responses.pop(base_result[0])

        return base_result[1], responses

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
        if base.additional_ids is None:
            base.additional_ids = []

        base.logo_landscape = base.logo_landscape or update.logo_landscape
        base.logo_portrait = base.logo_portrait or update.logo_portrait
        base.logo_square = base.logo_square or update.logo_square

        cls._merge_list(base.additional_ids, [update.id])
        cls._merge_list(base.genres, update.genres)
        cls._merge_list(base.devices, update.devices)
        cls._merge_list(base.modes, update.modes)
        cls._merge_list(base.languages, update.languages)
        cls._merge_list(base.platforms, update.platforms)
        cls._merge_list(base.player_modes, update.player_modes)
        cls._merge_list(base.tags, update.tags)

        cls._update_ratings(base.hist, update.hist)

        cls._update_availability(base, update)

    @classmethod
    def _update_availability(cls, base: Item, update: Item) -> None:
        """
        Update availability information in the base with information from
        the update.

        Args:
            base (Item): Base item to be updated.
            update (Item): Update item containing additional information.
        """
        if update.price is not None and update.price > 0:
            base.price = update.price

    @classmethod
    def _update_ratings(
        cls,
        base: list[RatingHist],
        update: list[RatingHist]
    ) -> None:
        """
        Update ratings in the base with those from the update.

        Args:
            base (List[RatingHist]): Base list of ratings.
            update (List[RatingHist]): Update list of ratings.
        """
        for update_rating in update:
            cls._update_single_rating(base, update_rating)

    @classmethod
    def _update_single_rating(
        cls,
        base: list[RatingHist],
        update_rating: RatingHist
    ) -> None:
        """
        Update a single rating in the base with the update.

        Args:
            base (List[RatingHist]): Base list of ratings.
            update_rating (RatingHist): Update rating to be merged
                into the base.
        """
        for base_rating in base:
            cls._merge_ratings(base_rating, update_rating)

    @classmethod
    def _merge_ratings(
        cls,
        base_rating: RatingHist,
        update_rating: RatingHist
    ) -> None:
        """
        Merge the votes from the update into the base rating.

        Args:
            base_rating (RatingHist): Base rating.
            update_rating (RatingHist): Update rating to be merged
                into the base.
        """
        if base_rating.rating == update_rating.rating:
            base_rating.votes += update_rating.votes
            return

    _KT = TypeVar("_KT")

    @classmethod
    def _merge_list(
        cls,
        base: list[_KT],
        update: list[_KT]
    ) -> None:
        """
        Update a list, ensuring no duplicate items are added.

        Args:
            base (list[str] | None): Base list to be updated.
            update (list[str] | None): Update list containing additional items.
        """
        base.extend(item for item in update if item not in base)
