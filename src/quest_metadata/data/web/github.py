from typing import Callable

from pydantic import BaseModel
from requests import Response, get
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from base.root_list_model import RootListModel
from utils.string_helper import to_camel

EXT_APPS: str = 'https://raw.githubusercontent.com/basti564' \
    + '/LauncherIcons/main/oculus_apps.json'


class GithubApp(BaseModel):
    """
    TODO
    """
    id: str
    app_name: str
    package_name: str

    class Config:
        """
        TODO
        """
        alias_generator: Callable[..., str] = to_camel


class GithubApps(RootListModel[GithubApp]):  # pylint: disable=too-few-public-methods
    """
    TODO
    """


@final
class GitHubWrapper(NonInstantiable):
    """
    TODO
    """

    _launch_method = "get_github_apps"

    @staticmethod
    def get_github_apps() -> GithubApps:
        '''
        Fetches the list of external applications from the specified URL.

        Returns:
            list[ExternalApp]:
                A list of dictionaries representing external applications.
        '''
        headers: dict[str, str] = {'Accept': 'application/json'}
        resp: Response = get(EXT_APPS, headers=headers, timeout=10)
        resp.encoding = 'utf8'
        data: GithubApps = GithubApps.model_validate(resp.json())
        return data
