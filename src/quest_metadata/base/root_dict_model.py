from typing import Iterator, Tuple, TypeVar

from pydantic import RootModel

_KT = TypeVar('_KT', bound=str)
_VT = TypeVar('_VT')


class RootDictModel(RootModel[dict[_KT, _VT]]):
    """
    TODO
    """

    root: dict[_KT, _VT] = {}

    def __getitem__(self, key: _KT) -> _VT:
        """
        TODO
        """
        return self.root[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """
        TODO
        """
        self.root[key] = value

    def __iter__(self) -> Iterator[_KT]:  # type: ignore
        """
        TODO
        """
        return iter(self.root)

    def __len__(self) -> int:
        """
        TODO
        """
        return len(self.root)

    def pop(self, key: _KT) -> _VT:
        """
        TODO
        """
        return self.root.pop(key)

    def keys(self) -> list[_KT]:
        """
        TODO
        """
        return list(self.root.keys())

    def values(self) -> list[_VT]:
        """
        TODO
        """
        return list(self.root.values())

    def items(self) -> list[Tuple[_KT, _VT]]:
        """
        TODO
        """
        return list(self.root.items())
