"""
base_class.py

This module defines the `BaseClass`, an abstract base class (ABC) intended
for subclassing.
Subclasses should inherit from this class and implement the necessary methods.

Attributes:
    logger (Logger): An instance of the Logger class for logging messages.

Example:
    ```python
    from base_module import BaseClass

    class MySubclass(BaseClass):
        def __init__(self) -> None:
            super().__init__()

        def custom_method(self) -> None:
            self.logger.info("Custom method executed.")
    ```
"""
from abc import ABC
from logging import Logger, getLogger


class BaseClass(ABC):
    """
    A base class that serves as an abstract base class (ABC).
    Subclasses should inherit from this class and implement the necessary
    methods.

    Attributes:
        logger (Logger): An instance of the Logger class for logging messages.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the BaseClass.

        It creates a Logger instance named after the current module (__name__)
        for logging messages related to this class.
        """
        self._logger: Logger = getLogger(self.__class__.__module__)
        super().__init__()
