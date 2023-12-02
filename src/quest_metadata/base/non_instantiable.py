from abc import ABC

from base.singleton import Singleton


class NonInstantiable(ABC, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]; pylint: disable=too-few-public-methods, line-too-long
    """
    TODO
    """
    _launch_method: str

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        """
        TODO
        """
        name: str = self.__class__.__name__
        raise TypeError(f"Cannot create instance of '{name}'. " +
                        f"Use {name}.{self._launch_method}()")
