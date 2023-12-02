from abc import ABCMeta
from typing import Any

from typing_extensions import Generic, TypeVar

_T = TypeVar("_T")


class Singleton(ABCMeta, Generic[_T]):
    """
    TODO
    """
    _instances: dict["Singleton[_T]", _T] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> _T:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
