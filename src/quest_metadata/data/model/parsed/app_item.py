"""
Module providing a model for parsing Oculus application items.

Classes:
- ParsedAppItem: Model representing a parsed Oculus application item.
"""
from pydantic import computed_field

from base.lists import LowerCaseUniqueList
from base.models import BaseModel
from data.model.oculus.app_versions import AppVersions


class ParsedAppItem(BaseModel):
    """
    Model representing a parsed Oculus application item.

    Attributes:
    - id (str): The ID of the application item.
    - name (str): The name of the application item.
    - packages (LowerCaseUniqueList): A list of unique lowercase package names.
    - versions (AppVersions | None): The versions of the application item.

    Computed Properties:
    - max_version_date: Property to get the maximum version date among the
        versions.
    """
    id: str
    name: str
    packages: LowerCaseUniqueList = LowerCaseUniqueList()
    versions: AppVersions | None = None

    @computed_field  # type: ignore[misc]
    @property
    def max_version_date(self) -> int:
        """
        Property to get the maximum version date among the versions.

        Returns:
        - int: The maximum version date.
        """
        if self.versions is None or len(self.versions) == 0:
            return 0
        return max(i.created_date for i in self.versions.root)
