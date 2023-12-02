from typing import Iterator, TypeVar

from pydantic import RootModel

_VT = TypeVar('_VT')


class RootListModel(RootModel[list[_VT]]):
    """
    TODO
    """

    root: list[_VT] = []

    def __getitem__(self, index: int) -> _VT:
        """
        TODO
        """
        return self.root[index]

    def __iter__(self) -> Iterator[_VT]:  # type: ignore
        """
        TODO
        """
        return iter(self.root)

    def __len__(self) -> int:
        """
        TODO
        """
        return len(self.root)

    def pop(self, index: int) -> _VT:
        """
        TODO
        """
        return self.root.pop(index)
