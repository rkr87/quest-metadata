from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.manager import AppManager
from data.web.github import GitHubWrapper


@final
class GithubUpdater(NonInstantiable):
    """
    TODO
    """
    _launch_method: str = "update"

    @staticmethod
    def update(app_manager: AppManager) -> None:
        """
        TODO
        """
        for item in GitHubWrapper.get_github_apps():
            app_manager.add(item.id, item.package_name, item.app_name)
        app_manager.save()
