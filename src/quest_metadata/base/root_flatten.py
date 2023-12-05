"""
root_flatten.py

This module defines a Pydantic model for representing a flattened
structure with a key (_key) and a value (_VT).

The `RootFlatten` class extends `RootModel` from Pydantic and is an abstract
base class (ABC). It provides behavior for validating and flattening data based
on the _key provided.

Attributes:
    _key (str): A string value indicating which key within the input dictionary
        will be flattened.

Usage:
    To use this model, create a subclass of `RootFlatten` and
    specify flattened type, specifying a key to be flattened.

    ```python
    from root_flatten import RootFlatten

    class MyFlattenModel(RootFlatten[int]):
        _key = 'my_key'

    my_flatten = MyFlattenModel.model_validate({'my_key': 0})

    print(f"my_flatten={my_flatten}")
    ```
Result:
    ```
    my_flatten=0
    ```

"""
from abc import ABC
from typing import ClassVar

from pydantic import validator
from typing_extensions import TypeVar

from base.base_model import RootModel

_VT = TypeVar('_VT')


class RootFlatten(ABC, RootModel[_VT]):
    """
    Pydantic model for representing a flattened structure with a key
    (_key) and a value (_VT).
    """
    _key: ClassVar
    root: _VT

    @validator("root", pre=True)
    @classmethod
    def flatten(cls, d: dict[str, _VT] | _VT) -> _VT:
        """
        Validate and flatten data based on the optional key.
        """
        if isinstance(d, dict):
            return d[cls._key]  # pyright: ignore[reportUnknownVariableType]
        return d
