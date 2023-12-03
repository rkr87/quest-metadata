# pyright: reportMissingTypeArgument=false
"""
non_instantiable.py

This module defines an abstract base class with a Singleton pattern,
preventing direct instantiation.

The `NonInstantiable` class should be subclassed, and instances should
be created using the specified launch method.

Attributes:
    _launch_method (str): The method to be used for creating instances.

Usage:
    To use this class, subclass it and define a launch method. Instances
    should be created using the launch method instead of directly
    instantiating the class.

    ```python
    from non_instantiable import NonInstantiable

    class MyNonInstantiableClass(NonInstantiable):
        _launch_method = "create_instance"

        @classmethod
        def create_instance(cls):
            return cls()
    ```

    Instances of `MyNonInstantiableClass` will be singletons, and
    direct instantiation will raise a `TypeError`.
"""
from abc import ABC

from base.singleton import Singleton


class NonInstantiable(ABC, metaclass=Singleton):  # pylint: disable=too-few-public-methods
    """
    An abstract base class with a Singleton pattern,
    preventing direct instantiation.

    This class should be subclassed, and instances should
    be created using the specified launch method.

    Attributes:
        _launch_method (str): The method to be used for creating instances.
    """
    _launch_method: str

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        """
        Constructor method that raises a TypeError.

        Raises:
            TypeError: If someone tries to create an instance directly.
        """
        name: str = self.__class__.__name__
        raise TypeError(f"Cannot create instance of '{name}'. " +
                        f"Use {name}.{self._launch_method}()")
