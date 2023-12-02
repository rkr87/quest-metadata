
from controller.github import GithubUpdater
from controller.processor import Processor
from data.local.manager import AppManager
from data.web.meta import MetaWrapper


def main() -> None:
    """
    TODO
    """
    app_manager: AppManager = AppManager()
    meta_wrapper: MetaWrapper = MetaWrapper()

    GithubUpdater.update(app_manager)
    Processor.start(app_manager, meta_wrapper)


if __name__ == "__main__":
    main()
