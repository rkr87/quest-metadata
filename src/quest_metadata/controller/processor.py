from typing_extensions import final

from base.non_instantiable import NonInstantiable
from data.local.manager import AppManager
from data.model.local_apps import LocalApps
from data.model.meta_response import MetaResponse
from data.web.meta import MetaWrapper

FILES: str = "./data/packages/"


@final
class Processor(NonInstantiable):
    '''
    Class representing a processor for managing applications.

    This class is designed to be used as a singleton.
    To create an instance, use the `start` class method.

    Attributes:
        apps (AppsManager):
            An instance of the AppsManager class for managing applications.
    '''
    _launch_method: str = "start"

    @staticmethod
    def start(app_manager: AppManager, meta_wrapper: MetaWrapper) -> None:
        '''
        Start the processor and initialize the AppsManager instance.

        Returns:
            None
        '''
        scrape_apps: LocalApps = app_manager.get(True)
        print(f"{len(scrape_apps)} to scrape")

        for k in list(scrape_apps.keys()):
            response: MetaResponse = meta_wrapper.get(k)
            text: str = response.model_dump_json(
                indent=4,
                exclude_unset=True,
                exclude_none=True
            )
            for p in scrape_apps[k].packages:
                with open(
                    f"{FILES}{p}.json", 'w', encoding="utf-8"
                ) as file:
                    file.write(text)
            app_manager.update(k)
            scrape_apps.pop(k)
