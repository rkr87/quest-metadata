"""
root_list_model.py

This module defines a Pydantic model for representing a list of values with
type (_VT).

The `RootListModel` class extends `RootModel` from Pydantic and is an abstract
base class (ABC). It provides behavior for interacting with lists.

Usage:
    To use this model, create a subclass of `RootListModel` specifying value
    type.

    ```python
    from root_list_model import RootListModel

    class MyListModel(RootListModel[str]):
        pass
    ```
"""
from abc import ABC
from typing import Iterator, TypeVar

from base.base_model import RootModel

_VT = TypeVar('_VT')


class RootListModel(ABC, RootModel[list[_VT]]):
    """
    Pydantic model for representing a list of values with type (_VT).
    """

    root: list[_VT] = []

    def __getitem__(self, index: int) -> _VT:
        """
        Get the value at the specified index.
        """
        return self.root[index]

    def __iter__(self) -> Iterator[_VT]:  # type: ignore
        """
        Return an iterator over the elements.
        """
        return iter(self.root)

    def __len__(self) -> int:
        """
        Return the number of elements in the list.
        """
        return len(self.root)

    def pop(self, index: int) -> _VT:
        """
        Remove and return the element at the specified index.
        """
        return self.root.pop(index)
