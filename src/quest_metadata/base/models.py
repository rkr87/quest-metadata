"""
Module providing base models for serialization and data manipulation.

Classes:
- BaseModel: A Pydantic BaseModel extension with asynchronous JSON saving.
- RootModel: A generic Pydantic RootModel extension with asynchronous
    JSON saving.
- RootDictModel: A RootModel extension for dictionary-like structures.
- RootListModel: A RootModel extension for list-like structures.
"""
from collections.abc import Iterator
from typing import Generic, TypeVar

import aiofiles
from pydantic import BaseModel as PydanticBaseModel
from pydantic import RootModel as PydanticRootModel

_VT = TypeVar("_VT")
_KT = TypeVar('_KT')


class BaseModel(PydanticBaseModel):
    """
    Pydantic BaseModel extension with asynchronous JSON saving.

    Methods:
    - save_json: Asynchronously saves the model as JSON to a file.

    Inherits from:
    - PydanticBaseModel
    """
    async def save_json(self, file_path: str) -> None:
        """
        Asynchronously saves the model as JSON to a file.

        Args:
        - file_path (str): The path to the file where the JSON will be saved.
        """
        json_text: str = self.model_dump_json(
            indent=4,
            exclude_none=True
        )
        async with aiofiles.open(file_path, 'w', encoding="utf-8") as file:
            await file.write(json_text)


class RootModel(BaseModel, PydanticRootModel[_VT], Generic[_VT]):
    """
    Generic Pydantic RootModel extension with asynchronous JSON saving.

    Inherits from:
    - BaseModel
    - PydanticRootModel[_VT]
    - Generic[_VT]
    """


class RootDictModel(RootModel[dict[_KT, _VT]]):
    """
    RootModel extension for dictionary-like structures.

    Methods:
    - __getitem__: Gets the value associated with a key.
    - __setitem__: Sets the value for a given key.
    - __iter__: Returns an iterator for the keys.
    - __len__: Returns the number of key-value pairs.
    - pop: Removes and returns the value associated with a key.
    - keys: Returns a list of keys.
    - values: Returns a list of values.
    - items: Returns a list of key-value pairs.
    - update: Updates the dictionary with key-value pairs from another
      RootDictModel.
    - get: Gets the value associated with a key, or None if not present.

    Inherits from:
    - RootModel[dict[_KT, _VT]]
    """
    root: dict[_KT, _VT] = {}

    def __getitem__(self, key: _KT) -> _VT:
        """
        Gets the value associated with a key.

        Args:
        - key (_KT): The key to retrieve the value for.

        Returns:
        - _VT: The value associated with the key.

        Raises:
        - KeyError: If the key is not present in the dictionary.
        """
        return self.root[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """
        Sets the value for a given key.

        Args:
        - key (_KT): The key to set the value for.
        - value (_VT): The value to set for the key.
        """
        self.root[key] = value

    def __iter__(self) -> Iterator[_KT]:  # type: ignore[override]
        """
        Returns an iterator for the keys.

        Returns:
        - Iterator[_KT]: An iterator for the keys in the dictionary.
        """
        return iter(self.root)

    def __len__(self) -> int:
        """
        Returns the number of key-value pairs.

        Returns:
        - int: The number of key-value pairs in the dictionary.
        """
        return len(self.root)

    def pop(self, key: _KT) -> _VT:
        """
        Removes and returns the value associated with a key.

        Args:
        - key (_KT): The key to remove from the dictionary.

        Returns:
        - _VT: The value associated with the removed key.

        Raises:
        - KeyError: If the key is not present in the dictionary.
        """
        return self.root.pop(key)

    def keys(self) -> list[_KT]:
        """
        Returns a list of keys.

        Returns:
        - list[_KT]: A list of keys in the dictionary.
        """
        return list(self.root.keys())

    def values(self) -> list[_VT]:
        """
        Returns a list of values.

        Returns:
        - list[_VT]: A list of values in the dictionary.
        """
        return list(self.root.values())

    def items(self) -> list[tuple[_KT, _VT]]:
        """
        Returns a list of key-value pairs.

        Returns:
        - list[tuple[_KT, _VT]]: A list of key-value pairs in the dictionary.
        """
        return list(self.root.items())

    def update(self, new_dict: "RootDictModel[_KT, _VT]") -> None:
        """
        Updates the dictionary with key-value pairs from another RootDictModel.

        Args:
        - new_dict (RootDictModel[_KT, _VT]): Another RootDictModel
            with key-value pairs.
        """
        self.root.update(new_dict)

    def get(self, key: _KT) -> None | _VT:
        """
        Gets the value associated with a key, or None if not present.

        Args:
        - key (_KT): The key to retrieve the value for.

        Returns:
        - None | _VT: The value associated with the key, or None if the key
            is not present.
        """
        return self.root.get(key)


class RootListModel(RootModel[list[_VT]]):
    """
    RootModel extension for list-like structures.

    Methods:
    - __getitem__: Gets the value at a specified index.
    - __iter__: Returns an iterator for the list.
    - __len__: Returns the number of elements in the list.
    - pop: Removes and returns the element at a specified index.
    - extend: Extends the list with elements from another RootListModel.

    Inherits from:
    - RootModel[list[_VT]]
    """
    root: list[_VT] = []

    def __getitem__(self, index: int) -> _VT:
        """
        Gets the value at a specified index.

        Args:
        - index (int): The index to retrieve the value from.

        Returns:
        - _VT: The value at the specified index.

        Raises:
        - IndexError: If the index is out of range.
        """
        return self.root[index]

    def __iter__(self) -> Iterator[_VT]:  # type: ignore[override]
        """
        Returns an iterator for the list.

        Returns:
        - Iterator[_VT]: An iterator for the elements in the list.
        """
        return iter(self.root)

    def __len__(self) -> int:
        """
        Returns the number of elements in the list.

        Returns:
        - int: The number of elements in the list.
        """
        return len(self.root)

    def pop(self, index: int) -> _VT:
        """
        Removes and returns the element at a specified index.

        Args:
        - index (int): The index to remove the element from.

        Returns:
        - _VT: The element at the specified index.

        Raises:
        - IndexError: If the index is out of range.
        """
        return self.root.pop(index)

    def extend(
        self,
        new_list: "RootListModel[_VT]",
        ignore_dupes: bool = False
    ) -> None:
        """
        Extends the list with elements from another RootListModel.

        Args:
        - new_list (RootListModel[_VT]): Another RootListModel with elements
            to be added.
        - ignore_dupes (bool): If True, ignores duplicate elements during
            extension.
        """
        if ignore_dupes:
            self.root.extend([i for i in new_list if i not in self.root])
        self.root.extend(new_list)
