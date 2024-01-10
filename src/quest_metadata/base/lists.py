"""
Module providing a ValidatedList class and its subclasses for handling
validated lists.

Classes:
- ValidatedList: An abstract base class for lists that validate their elements.
- UniqueList: A subclass of ValidatedList ensuring unique elements.
- LowerCaseUniqueList: A subclass of UniqueList ensuring case-insensitive
    uniqueness for string elements.
"""
from abc import ABC, abstractmethod
from collections import UserList
from collections.abc import Iterable
from typing import Any, Generic, Self, SupportsIndex, TypeVar, overload

from pydantic import GetCoreSchemaHandler
from pydantic_core import SchemaSerializer, core_schema

_VT = TypeVar("_VT")


class ValidatedList(UserList[_VT], Generic[_VT], ABC):
    """
    Abstract base class for lists that validate their elements.

    Methods:
    - __init__: Initializes the ValidatedList with optional initial values.
    - append: Appends a validated element to the list.
    - insert: Inserts a validated element at a specified position.
    - extend: Extends the list with validated elements from another iterable.
    - __add__: Returns a new ValidatedList containing validated elements
      from the current list and another iterable.
    - __iadd__: Extends the current list with validated elements from another
      iterable.
    - __radd__: Extends another iterable with validated elements from the
      current list.
    - __setitem__: Sets a validated element at a specified index or slice.

    Abstract Methods:
    - _validate_value: Validates a single element and returns it if valid,
      or None if invalid.
    - __get_pydantic_core_schema__: Provides Pydantic core schema information
      for the class.

    Static Methods:
    - _to_list: Converts a single value or iterable to a list of validated
      elements.
    """

    def __init__(
        self,
        initlist: Iterable[_VT | None] | None = None
    ) -> None:
        self.data = []
        validated: list[_VT] = self._validate_values(self._to_list(initlist))
        super().__init__(validated)

    def append(self, item: _VT | None) -> None:
        if (x := self._validate_value(item)) is not None:
            super().append(x)

    def insert(self, i: int, item: _VT | None) -> None:
        if (x := self._validate_value(item)) is not None:
            super().insert(i, x)

    def extend(self, other: Iterable[_VT | None]) -> None:
        super().extend(self._validate_values(other))

    def __add__(self, other: Iterable[_VT | None] | None) -> Self:
        validated: list[_VT] = self._validate_values(self._to_list(other))
        return super().__add__(validated)

    def __iadd__(self, values: Iterable[_VT | None] | None) -> Self:
        validated: list[_VT] = self._validate_values(self._to_list(values))
        return super().__iadd__(self._validate_values(validated))

    def __radd__(self, values: Iterable[_VT | None] | None) -> Self:
        validated: list[_VT] = self._validate_values(self._to_list(values))
        return super().__iadd__(self._validate_values(validated))

    @overload
    def __setitem__(self, i: SupportsIndex, item: _VT | None) -> None: ...

    @overload
    def __setitem__(self, i: slice, item: Iterable[_VT | None]) -> None: ...

    def __setitem__(
        self,
        i: SupportsIndex | slice,
        item: Iterable[_VT | None] | _VT | None
    ) -> None:
        if item is None:
            return
        if isinstance(i, slice):
            validated: list[_VT] = self._validate_values(self._to_list(item))
            super().__setitem__(i, validated)
            return
        if (
            (x := self._validate_value(item)) is not None  # type: ignore[arg-type]
        ):
            super().__setitem__(i, x)

    def _validate_values(self, values: Iterable[_VT | None]) -> list[_VT]:
        """
        Validates a list of elements.

        Args:
        - values: The elements to be validated.

        Returns:
        - list[_VT]: The list of validated elements.
        """
        return [y for x in values if (y := self._validate_value(x))]

    @abstractmethod
    def _validate_value(self, value: _VT | None) -> _VT | None:
        """
        Validates a single element.

        Args:
        - value: The element to be validated.

        Returns:
        - _VT | None: The validated element or None if invalid.
        """

    @staticmethod
    def _to_list(
        value: Iterable[_VT | None] | _VT | None
    ) -> list[_VT | None]:
        """
        Converts a single value or iterable to a list of validated elements.

        Args:
        - value: The value or iterable to be converted.

        Returns:
        - list[_VT | None]: The list of validated elements.
        """
        if value is None:
            return []
        if isinstance(value, Iterable):
            return list(value)  # pyright: ignore[reportUnknownArgumentType]
        return [value]

    @classmethod
    def __get_pydantic_core_schema__(  # type: ignore[misc] # pylint: disable=w3201
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Provides Pydantic core schema information for the class.

        Args:
        - source_type: The type for which the core schema is generated.
        - handler: The Pydantic core schema handler.

        Returns:
        - CoreSchema: The generated core schema.
        """
        _ = source_type
        schema: core_schema.AfterValidatorFunctionSchema = \
            core_schema.no_info_after_validator_function(
                cls,
                handler(set),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    set,
                    info_arg=False,
                    return_schema=core_schema.set_schema(),
                ),
            )
        cls.__pydantic_serializer__ = SchemaSerializer(schema)  # type: ignore[attr-defined]
        return schema


class UniqueList(ValidatedList[_VT]):
    """
    Subclass of ValidatedList ensuring unique elements.

    Methods:
    - _validate_value: Validates a single element and ensures uniqueness.

    Inherits from:
    - ValidatedList
    """

    def _validate_value(self, value: _VT | None) -> _VT | None:
        """
        Validates a single element and ensures uniqueness.

        Args:
        - value: The element to be validated.

        Returns:
        - _VT | None: The validated element or None if invalid.
        """
        if not value or value in self:
            return None
        return value


class LowerCaseUniqueList(UniqueList[str]):
    """
    Subclass of UniqueList ensuring case-insensitive uniqueness for string
    elements.

    Methods:
    - _validate_value: Validates a single string element with case-insensitive
      uniqueness.

    Inherits from:
    - UniqueList
    """

    def _validate_value(self, value: str | None) -> str | None:
        """
        Validates a single string element with case-insensitive uniqueness.

        Args:
        - value: The string element to be validated.

        Returns:
        - str | None: The validated string element or None if invalid.
        """
        if not value:
            return None
        return super()._validate_value(value.lower())
