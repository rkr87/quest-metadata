from pydantic import BaseModel

from base.root_dict_model import RootDictModel


class LocalApp(BaseModel):
    """
    TODO
    """
    packages: list[str]
    app_name: str
    added: str
    updated: str | None = None


class LocalApps(RootDictModel[str, LocalApp]):  # pylint: disable=too-few-public-methods
    """
    TODO
    """
