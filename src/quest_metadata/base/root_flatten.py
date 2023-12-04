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
from typing import ClassVar, Union

from pydantic import validator
from typing_extensions import TypeVar

from base.base_model import RootModel

_VT = TypeVar('_VT')


class RootFlatten(ABC, RootModel[Union[_VT, None]]):
    """
    Pydantic model for representing a flattened structure with a key
    (_key) and a value (_VT).
    """
    _key: ClassVar
    root: _VT | None

    @validator("root", pre=True)
    @classmethod
    def flatten(cls, d: dict[str, _VT] | None) -> _VT | None:
        """
        Validate and flatten data based on the optional key.
        """
        if d is None:
            return None
        if d.get(cls._key) is None:
            return None
        return d[cls._key]
