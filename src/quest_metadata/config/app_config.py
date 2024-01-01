from base.models import SingletonModel


class AppConfig(SingletonModel):
    logging_config: str = ".config_app/logging.conf"
    scrape_locale: str = "en_US"
    data_path: str = ".data"
    resource_path: str = ".res"
