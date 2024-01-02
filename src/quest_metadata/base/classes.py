"""
Module providing utility classes for common design patterns and base
functionality.

Classes:
- NonInstantiable: An abstract base class to prevent instantiation,
    requiring subclasses to define the '_launch_method' attribute for
    proper instantiation.
- BaseClass: An abstract base class providing basic functionality and
    a logger instance for subclasses.
- SingletonMeta: Metaclass for implementing the Singleton pattern,
    ensuring that only one instance of a class is created.
- Singleton: A singleton class inheriting from BaseClass and using
    SingletonMeta as its metaclass.
"""
from abc import ABC, ABCMeta
from logging import Logger, getLogger
from typing import Any, Generic, Self, TypeVar

_T = TypeVar("_T")


class NonInstantiable(ABC):
    """
    An abstract base class to prevent instantiation. Subclasses must define
    the '_launch_method' attribute to specify the method for instantiation.

    Attributes:
    - _launch_method (str): The method to be used for instantiation.
    """
    _launch_method: str

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        """
        Raises:
        - TypeError: If an attempt is made to create an instance.
        """
        name: str = self.__class__.__name__
        raise TypeError(f"Cannot create instance of '{name}'. " +
                        f"Use {name}.{self._launch_method}()")


class BaseClass(ABC):
    """
    An abstract base class providing basic functionality for subclasses.

    Attributes:
    - _logger (Logger): The logger instance for the class.
    """

    def __init__(self) -> None:
        self._logger: Logger = getLogger(self.__class__.__module__)
        super().__init__()


class SingletonMeta(ABCMeta, Generic[_T]):
    """
    Metaclass for implementing the Singleton pattern.

    Attributes:
    - _instances (dict): A dictionary to store singleton instances.
    """
    _instances: dict["SingletonMeta[_T]", _T] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> _T:
        """
        Creates a singleton instance if it does not exist, or returns the
        existing instance.

        Returns:
        - _T: The singleton instance.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def add_instance(cls, instance: Any) -> _T:
        """
        Add a new instance to the singleton registry.

        Args:
        - instance (Any): The instance to add.

        Returns:
        - _T: The added singleton instance.
        """
        if cls not in cls._instances and isinstance(instance, cls):
            cls._instances[cls] = instance
        return cls._instances[cls]

    def instance_exists(cls) -> bool:
        """
        Check if a singleton instance exists.

        Returns:
        - bool: True if a singleton instance exists, False otherwise.
        """
        return cls in cls._instances

    def get_instance(cls) -> _T:
        """
        Get the existing singleton instance.

        Returns:
        - _T: The existing singleton instance.
        """
        return cls._instances[cls]


class Singleton(BaseClass, metaclass=SingletonMeta):   # pyright: ignore[reportMissingTypeArgument]
    """
    A singleton class that inherits from BaseClass and uses SingletonMeta
    as its metaclass.
    """
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # pylint: disable=W0613
        """
        Create a new instance of the singleton class if it doesn't exist,
        or return the existing instance.

        Returns:
        - Singleton: The singleton instance.
        """
        if cls.instance_exists():
            return cls.get_instance()  # type: ignore[return-value]
        return cls.add_instance(super().__new__(cls))  # type: ignore[return-value]
