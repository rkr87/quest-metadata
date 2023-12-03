"""
meta_cookie.py

This module defines the MetaCookie class, responsible for fetching and
returning the required cookie for interacting with the Meta API.

Usage:
    To use the MetaCookie, call the `fetch` method, which opens a browser,
    navigates to the Meta domain, handles cookie consent, and waits until the
    required 'gu' cookie is available.

    Example:
    ```python
    from data.web.meta_cookie import MetaCookie

    # Fetch the required Meta cookie
    meta_cookie = MetaCookie.fetch()

    # Use the obtained cookie for Meta API requests
    print(meta_cookie)
    ```

Attributes:
    META_DOMAIN (str): The base URL of the Meta domain.
"""
from logging import Logger, getLogger
from time import sleep

from playwright.sync_api import sync_playwright
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from constants.constants import META_DOMAIN


@final
class MetaCookie(NonInstantiable):
    """
    MetaCookie class for fetching the required cookie for interacting with the
    Meta API.

    Attributes:
        _launch_method (str): The method to be used for creating instances.
    """
    _launch_method = "fetch"

    @staticmethod
    def fetch() -> str:
        """
        Fetch the required cookie for interacting with the Meta API.

        Returns:
            str: The obtained cookie.
        """
        logger: Logger = getLogger(__name__)
        logger.info("Acquiring cookies from meta.com")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(META_DOMAIN)
            consent = page.wait_for_selector("text=Allow all cookies")
            sleep(2)
            if consent is not None:
                consent.click(force=True)
            while 'gu' not in [c['name'] for c in context.cookies()]:
                logger.debug("Waiting for 'gu' cookie...")
                sleep(1)
            cookies: str = ";".join(
                [f"{c['name']}={c['value']}" for c in context.cookies()]
            )
            return cookies
