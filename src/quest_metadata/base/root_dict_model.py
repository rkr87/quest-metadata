"""
root_dict_model.py

This module defines a Pydantic model for representing a dictionary with key
(_KT) and value (_VT) types.

The `RootDictModel` class extends `RootModel` from Pydantic and is an abstract
base class (ABC). It provides behavior for interacting with dictionaries.

Usage:
    To use this model, create a subclass of `RootDictModel` and specify key
    and value types.

    ```python
    from root_dict_model import RootDictModel

    class MyDictModel(RootDictModel[str, int]):
        pass
    ```
"""
from abc import ABC
from collections.abc import Iterator
from typing import TypeVar

from base.base_model import RootModel

_KT = TypeVar('_KT', bound=str)
_VT = TypeVar('_VT')


class RootDictModel(ABC, RootModel[dict[_KT, _VT]]):
    """
    Pydantic model for representing a dictionary with key (_KT) and value (_VT)
    types.
    """

    root: dict[_KT, _VT] = {}

    def __getitem__(self, key: _KT) -> _VT:
        """
        Get the value associated with the specified key.
        """
        return self.root[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """
        Set the value for the specified key.
        """
        self.root[key] = value

    def __iter__(self) -> Iterator[_KT]:  # type: ignore[override]
        """
        Return an iterator over the keys.
        """
        return iter(self.root)

    def __len__(self) -> int:
        """
        Return the number of key-value pairs in the dictionary.
        """
        return len(self.root)

    def pop(self, key: _KT) -> _VT:
        """
        Remove the specified key and return its value.
        """
        return self.root.pop(key)

    def keys(self) -> list[_KT]:
        """
        Return a list of all keys in the dictionary.
        """
        return list(self.root.keys())

    def values(self) -> list[_VT]:
        """
        Return a list of all values in the dictionary.
        """
        return list(self.root.values())

    def items(self) -> list[tuple[_KT, _VT]]:
        """
        Return a list of all key-value pairs in the dictionary.
        """
        return list(self.root.items())
