"""
base_model.py

This module defines custom Pydantic models for data validation and
manipulation.
"""
from typing import Generic, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import RootModel as PydanticRootModel

_VT = TypeVar("_VT")


class BaseModel(PydanticBaseModel):
    """Base class for Pydantic models with additional utility methods."""

    def save_json(self, file_path: str) -> None:
        """
        Save the JSON representation of the model to a file.

        Parameters:
            file_path (str): The path to the file where JSON should be saved.
        """
        json_text: str = self.model_dump_json(
            indent=4,
            exclude_unset=True,
            exclude_none=True
        )
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(json_text)


class RootModel(BaseModel, PydanticRootModel[_VT], Generic[_VT]):
    """
    Root model class combining features of BaseModel and PydanticRootModel.

    Parameters:
        _VT: Type variable for PydanticRootModel.
    """
