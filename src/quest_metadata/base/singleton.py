"""
singleton.py

This module defines a generic Singleton metaclass.

The Singleton metaclass ensures that only one instance of a class is created.
Instances of the class are stored in a dictionary, and the metaclass controls
the creation and retrieval of instances, ensuring that only a single instance
exists for each class.

Attributes:
    _instances (dict): A dictionary mapping class types to their instances.

Usage:
    To use this metaclass, declare a class with `metaclass=Singleton`:

    ```python
    class MyClass(metaclass=Singleton):
        pass
    ```
    Instances of `MyClass` will be singletons, and subsequent calls to create
    instances will return the existing instance.
"""
from abc import ABCMeta
from typing import Any

from typing_extensions import Generic, TypeVar

_T = TypeVar("_T")


class Singleton(ABCMeta, Generic[_T]):
    """
    A generic Singleton metaclass.

    This metaclass ensures that only one instance of a class is created.

    Attributes:
        _instances (dict): A dictionary mapping class types to their instances.
    """
    _instances: dict["Singleton[_T]", _T] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> _T:
        """
        Call method to create an instance of the class if it does not exist,
        and return the existing instance otherwise.

        Args:
            *args (Any): Variable arguments.
            **kwargs (Any): Keyword arguments.

        Returns:
            _T: An instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
