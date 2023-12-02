from typing import ClassVar, Union

from pydantic import RootModel, validator
from typing_extensions import TypeVar

_VT = TypeVar('_VT')


class RootFlatten(RootModel[Union[_VT, None]]):
    """
    TODO
    """
    _key: ClassVar = None
    root: _VT | None

    @validator("root", pre=True)
    @classmethod
    def convert_data(cls, d: dict[str, _VT] | None) -> _VT | None:
        """
        TODO
        """
        if d is None:
            return None
        if cls._key is None:
            if len(d) == 1:
                for _, v in d.items():
                    return v
            return None
        if d.get(cls._key) is not None:
            return d[cls._key]
        return None
