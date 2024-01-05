"""
Module providing a Parser utility class for parsing and consolidating data from
multiple OculusApp instances.

Classes:
- Parser: Utility class for parsing and consolidating data.
"""
from logging import Logger, getLogger
from typing import TypeVar

from typing_extensions import final

from base.classes import NonInstantiable
from data.model.oculus.app import Item, OculusApp, RatingHist
from utils.error_manager import ErrorManager


@final
class Parser(NonInstantiable):
    """
    Utility class for parsing and consolidating data from multiple sources.

    This class provides methods for parsing and consolidating data from
    multiple OculusApp instances. It is designed to handle errors in the
    response and merge data fields from different sources.

    Methods:
    - parse: Parse and consolidate data from primary and additional OculusApp
        instances.
    - _handle_errors: Handle errors in the response and log them.
    - _consolidate_results: Consolidate data fields from the base and update
        Item instances.
    - _update_ratings: Update the ratings history list.
    - _update_single_rating: Update a single rating entry in the ratings
        history list.
    - _merge_ratings: Merge ratings from two RatingHist instances.
    - _merge_list: Merge lists while avoiding duplicates.

    Attributes:
    - _launch_method (str): The launch method for parsing, set to "parse".
    """
    _launch_method: str = "parse"

    @classmethod
    def parse(
        cls,
        primary: OculusApp,
        additional: list[OculusApp],
        package: str
    ) -> OculusApp:
        """
        Parse and consolidate data from primary and additional OculusApp
        instances.

        Args:
        - primary (OculusApp): The primary OculusApp instance.
        - additional (list[OculusApp]): List of additional OculusApp instances.
        - package (str): The package identifier.

        Returns:
        - OculusApp: The consolidated OculusApp instance.
        """
        for merge in additional:
            cls._consolidate_results(primary.data, merge.data)
        cls._handle_errors(primary, package)
        primary.package = package
        return primary

    @classmethod
    def _handle_errors(cls, response: OculusApp, package: str) -> None:
        """
        Handle errors in the response and log them.

        Args:
        - response (OculusApp): The OculusApp instance representing the
            response.
        - package (str): The package identifier.
        """
        if len(response.errors) == 0:
            return
        error: str = ErrorManager().capture(
            "ValidationError",
            "Parsing Oculus App Response",
            f"App Response contains errors: {package}",
            error_info={
                "package": package,
                "errors": response.errors,
                "data": response.data.model_dump()
            }
        )
        logger: Logger = getLogger(__name__)
        logger.warning("%s", error)

    @classmethod
    def _consolidate_results(cls, base: Item, update: Item) -> None:
        """
        Consolidate data fields from the base and update Item instances.

        Args:
        - base (Item): The base Item instance.
        - update (Item): The update Item instance.
        """
        base.additional_ids = base.additional_ids or []

        base.app_images = base.app_images or update.app_images
        base.translations = base.translations or update.translations

        cls._merge_list(base.additional_ids, [update.id])
        cls._merge_list(base.genres, update.genres)
        cls._merge_list(base.devices, update.devices)
        cls._merge_list(base.modes, update.modes)
        cls._merge_list(base.languages, update.languages)
        cls._merge_list(base.platforms, update.platforms)
        cls._merge_list(base.player_modes, update.player_modes)
        cls._merge_list(base.tags, update.tags)
        cls._merge_list(base.keywords, update.keywords)

        cls._update_ratings(base.hist, update.hist)

    @classmethod
    def _update_ratings(
        cls,
        base: list[RatingHist],
        update: list[RatingHist]
    ) -> None:
        """
        Update the ratings history list.

        Args:
        - base (list[RatingHist]): The base ratings history list.
        - update (list[RatingHist]): The update ratings history list.
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
        Update a single rating entry in the ratings history list.

        Args:
        - base (list[RatingHist]): The base ratings history list.
        - update_rating (RatingHist): The update RatingHist instance.
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
        Merge ratings from two RatingHist instances.

        Args:
        - base_rating (RatingHist): The base RatingHist instance.
        - update_rating (RatingHist): The update RatingHist instance.
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
        Merge lists while avoiding duplicates.

        Args:
        - base (list[_KT]): The base list.
        - update (list[_KT]): The update list.
        """
        base.extend(item for item in update if item not in base)
